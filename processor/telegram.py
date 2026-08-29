#!/usr/bin/env python3
"""
Telegram upload utilities for Hardsub Platform
Uploads processed videos to Telegram using Bot API
"""

import os
import json
from pathlib import Path
from datetime import datetime


def format_caption(title, job_id, subtitle_config, video_info):
    """
    Format Telegram message caption.
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
    
    caption = (
        f"🎬 {title}\n\n"
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
    Upload video to Telegram using Bot API.
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
    
    # Check file size (Telegram limit: 50MB for regular bots, 2GB for premium)
    file_size = video_path.stat().st_size
    max_size = 52428800  # 50MB
    
    if file_size > max_size:
        return {
            'success': False,
            'error': f'File too large for Telegram: {file_size / (1024*1024):.1f}MB (max 50MB)'
        }
    
    caption = format_caption(title, job_id, subtitle_config, video_info)
    
    try:
        import urllib.request
        import urllib.parse
        
        # Use sendVideo endpoint
        url = f"https://api.telegram.org/bot{token}/sendVideo"
        
        # Prepare multipart form data
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        
        # Read video file
        with open(video_path, 'rb') as f:
            video_data = f.read()
        
        # Build multipart body
        body_parts = []
        
        # Add chat_id
        body_parts.append(f'--{boundary}'.encode())
        body_parts.append(b'Content-Disposition: form-data; name="chat_id"\r\n')
        body_parts.append(chat_id.encode())
        
        # Add caption
        body_parts.append(f'--{boundary}'.encode())
        body_parts.append(b'Content-Disposition: form-data; name="caption"\r\n')
        body_parts.append(caption.encode('utf-8'))
        
        # Add parse_mode for formatting
        body_parts.append(f'--{boundary}'.encode())
        body_parts.append(b'Content-Disposition: form-data; name="parse_mode"\r\n')
        body_parts.append(b'HTML')
        
        # Add video file
        body_parts.append(f'--{boundary}'.encode())
        body_parts.append(
            f'Content-Disposition: form-data; name="video"; filename="{video_path.name}"'.encode()
        )
        body_parts.append(b'Content-Type: video/mp4\r\n')
        body_parts.append(video_data)
        
        # Final boundary
        body_parts.append(f'--{boundary}--'.encode())
        
        # Join with CRLF
        body = b'\r\n'.join(body_parts)
        
        # Make request
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                'Content-Type': f'multipart/form-data; boundary={boundary}',
                'Content-Length': str(len(body))
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=600) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get('ok'):
                message_id = result.get('result', {}).get('message_id')
                
                # Construct message link
                chat_id_str = str(chat_id)
                if chat_id_str.startswith('-100'):
                    # Supergroup/channel
                    message_link = f"https://t.me/c/{chat_id_str[4:]}/{message_id}"
                elif chat_id_str.startswith('-'):
                    # Private group
                    message_link = None  # Can't construct direct link for private groups
                else:
                    # Public username or channel
                    message_link = None
                
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
