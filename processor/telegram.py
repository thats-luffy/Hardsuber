#!/usr/bin/env python3
"""
Telegram upload utilities for Hardsub Platform
Uploads processed videos to Telegram using Bot API with streaming support
Does NOT load entire video into RAM - uses chunked/multipart upload
"""

import os
import json
from pathlib import Path
from datetime import datetime


def format_caption(title, job_id, subtitle_config, video_info):
    """
    Format Telegram message caption with proper HTML escaping.
    """
    font_name = subtitle_config.get('fontFamily', 'Vazirmatn')
    width = video_info.get('width', 0)
    height = video_info.get('height', 0)
    duration = video_info.get('duration', 0)
    
    # Format duration as HH:MM:SS
    hours = int(duration // 3600)
    minutes = int((duration % 3600) // 60)
    seconds = int(duration % 60)
    duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    # Escape special HTML characters in title
    escaped_title = title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    caption = (
        f"🎬 {escaped_title}\n\n"
        f"🆔 Job: {job_id}\n\n"
        f"✅ هاردساب تکمیل شد\n"
        f"🔤 فونت: {font_name}\n"
        f"📐 رزولوشن: {width}x{height}\n"
        f"⏱ مدت: {duration_str}"
    )
    
    # Ensure caption is within Telegram's 1024 character limit
    return caption[:1024]


def upload_to_telegram(video_path, title, job_id, subtitle_config, video_info):
    """
    Upload video to Telegram using Bot API with streaming multipart upload.
    Does NOT load entire file into memory.
    Returns dict with success status and message info.
    """
    token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')
    
    if not token or not chat_id:
        return {
            'success': False,
            'error': 'Telegram credentials not configured'
        }
    
    video_path = Path(video_path)
    
    if not video_path.exists():
        return {
            'success': False,
            'error': 'Video file not found'
        }
    
    # Check file size (Telegram limit: 50MB for regular bots, 2GB for premium bots)
    file_size = video_path.stat().st_size
    max_size = 52428800  # 50MB (standard bot limit)
    
    # Note: Premium bots can handle up to 2GB, but we use 50MB as default
    # Users with premium bots can increase MAX_TELEGRAM_SIZE env var
    max_size = int(os.environ.get('MAX_TELEGRAM_SIZE', str(max_size)))
    
    if file_size > max_size:
        return {
            'success': False,
            'error': f'File too large for Telegram: {file_size / (1024*1024):.1f}MB (max {max_size / (1024*1024):.0f}MB)'
        }
    
    caption = format_caption(title, job_id, subtitle_config, video_info)
    
    try:
        import urllib.request
        
        # Use sendVideo endpoint
        url = f"https://api.telegram.org/bot{token}/sendVideo"
        
        # Generate boundary for multipart form data
        import secrets
        boundary = '----WebKitFormBoundary' + secrets.token_hex(16)
        
        # Build multipart body manually with streaming
        body_parts = []
        
        # Add chat_id
        body_parts.append(f'--{boundary}'.encode())
        body_parts.append(b'Content-Disposition: form-data; name="chat_id"\r\n')
        body_parts.append(chat_id.encode())
        
        # Add caption
        body_parts.append(f'--{boundary}'.encode())
        body_parts.append(b'Content-Disposition: form-data; name="caption"\r\n')
        body_parts.append(caption.encode('utf-8'))
        
        # Add parse_mode for HTML formatting
        body_parts.append(f'--{boundary}'.encode())
        body_parts.append(b'Content-Disposition: form-data; name="parse_mode"\r\n')
        body_parts.append(b'HTML')
        
        # Add video file header
        body_parts.append(f'--{boundary}'.encode())
        body_parts.append(
            f'Content-Disposition: form-data; name="video"; filename="{video_path.name}"'.encode()
        )
        body_parts.append(b'Content-Type: video/mp4\r\n')
        
        # Calculate total body size
        headers_size = sum(len(part) + 2 for part in body_parts)  # +2 for CRLF
        footers_size = len(f'\r\n--{boundary}--\r\n'.encode())
        
        # Open file and calculate total size
        with open(video_path, 'rb') as f:
            pass  # File exists check already done
        
        total_size = headers_size + file_size + footers_size
        
        # Create a custom reader class for streaming upload
        class MultipartReader:
            def __init__(self, parts, file_path, boundary):
                self.parts = iter(parts)
                self.file_path = file_path
                self.boundary = boundary
                self.file = None
                self.done = False
            
            def read(self, size=-1):
                # First return all pre-file parts
                if self.file is None:
                    for part in self.parts:
                        return part + b'\r\n'
                    
                    # All parts returned, now open file
                    self.file = open(self.file_path, 'rb')
                    return b''
                
                # Read from file
                if size == -1:
                    data = self.file.read()
                    self.file.close()
                    self.done = True
                    # Add footer
                    footer = f'\r\n--{self.boundary}--\r\n'.encode()
                    return data + footer
                
                data = self.file.read(size)
                if not data:
                    self.file.close()
                    self.done = True
                    footer = f'\r\n--{self.boundary}--\r\n'.encode()
                    return footer
                return data
        
        # For simplicity, we'll use a different approach - read in chunks
        # This avoids loading entire file into memory at once
        
        # Actually, let's use requests-like behavior with urllib
        # We'll build the body incrementally
        
        # Simple approach: use file object directly in urlopen
        # This requires building headers first
        
        # Build the request with proper Content-Length
        req = urllib.request.Request(url, method='POST')
        req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
        
        # Create generator for streaming body
        def body_generator():
            # Send headers
            for part in body_parts:
                yield part + b'\r\n'
            
            # Stream file content in chunks
            chunk_size = 8192
            with open(video_path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    yield chunk
            
            # Send footer
            yield f'\r\n--{boundary}--\r\n'.encode()
        
        # For urllib, we need to provide the full body
        # Since we want to avoid loading everything into memory,
        # we'll use a workaround with a custom file-like object
        
        class StreamingBody:
            def __init__(self, parts, file_path, boundary):
                self.parts_iter = iter(parts)
                self.file_path = file_path
                self.boundary = boundary
                self.file = None
                self.current_part = None
                self.part_offset = 0
                self.footer_sent = False
            
            def read(self, size=-1):
                result = b''
                
                while len(result) < (size if size > 0 else float('inf')):
                    # Get current part if needed
                    if self.current_part is None:
                        try:
                            self.current_part = next(self.parts_iter) + b'\r\n'
                            self.part_offset = 0
                        except StopIteration:
                            # All parts done, open file
                            if self.file is None:
                                self.file = open(self.file_path, 'rb')
                            else:
                                # File done, send footer
                                if not self.footer_sent:
                                    self.footer_sent = True
                                    return result + f'\r\n--{self.boundary}--\r\n'.encode()
                                return result if result else None
                    
                    if self.current_part:
                        chunk = self.current_part[self.part_offset:]
                        if size > 0 and len(result) + len(chunk) > size:
                            chunk = chunk[:size - len(result)]
                            self.part_offset += len(chunk)
                            result += chunk
                            if self.part_offset >= len(self.current_part):
                                self.current_part = None
                        else:
                            result += chunk
                            self.current_part = None
                    elif self.file:
                        chunk = self.file.read(size - len(result) if size > 0 else 8192)
                        if not chunk:
                            self.file.close()
                            self.file = None
                        else:
                            result += chunk
                    else:
                        if not self.footer_sent:
                            self.footer_sent = True
                            return result + f'\r\n--{self.boundary}--\r\n'.encode()
                        return result if result else None
                
                return result if result else None
        
        body_reader = StreamingBody(body_parts, video_path, boundary)
        
        # Make request with streaming body
        req.data = body_reader
        req.add_header('Content-Length', str(total_size))
        
        with urllib.request.urlopen(req, timeout=600) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get('ok'):
                message_id = result.get('result', {}).get('message_id')
                
                # Construct message link
                chat_id_str = str(chat_id)
                message_link = None
                if chat_id_str.startswith('-100'):
                    # Supergroup/channel
                    message_link = f"https://t.me/c/{chat_id_str[4:]}/{message_id}"
                elif not chat_id_str.startswith('-'):
                    # Public username
                    message_link = f"https://t.me/{chat_id}/{message_id}"
                
                return {
                    'success': True,
                    'message_id': message_id,
                    'message_link': message_link,
                    'response': result
                }
            else:
                error_desc = result.get('description', 'Unknown error')
                return {
                    'success': False,
                    'error': f'Telegram API error: {error_desc}'
                }
    
    except Exception as e:
        return {
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }


def send_message(text, parse_mode='HTML'):
    """
    Send a text message to Telegram (for testing/debugging).
    """
    token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')
    
    if not token or not chat_id:
        return {'success': False, 'error': 'Telegram credentials not configured'}
    
    try:
        import urllib.request
        import json
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        data = json.dumps({
            'chat_id': chat_id,
            'text': text,
            'parse_mode': parse_mode
        }).encode('utf-8')
        
        req = urllib.request.Request(
            url,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result if result.get('ok') else {'success': False, 'error': result}
    
    except Exception as e:
        return {'success': False, 'error': str(e)}
