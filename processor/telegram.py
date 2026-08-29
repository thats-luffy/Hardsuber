"""
Telegram upload utilities.
Uploads processed videos to Telegram using Bot API.
"""

import os
import asyncio
from pathlib import Path


def upload_to_telegram(bot_token: str, chat_id: str, video_path: Path, caption: str = "") -> tuple[bool, str]:
    """
    Upload video to Telegram channel/group.
    
    Args:
        bot_token: Telegram bot token
        chat_id: Target chat ID
        video_path: Path to video file
        caption: Optional caption text
        
    Returns:
        Tuple of (success: bool, message_link: str)
    """
    try:
        # Use synchronous wrapper for async function
        return asyncio.run(_upload_async(bot_token, chat_id, video_path, caption))
    except Exception as e:
        print(f"Telegram upload error: {e}")
        return False, ""


async def _upload_async(bot_token: str, chat_id: str, video_path: Path, caption: str) -> tuple[bool, str]:
    """Async implementation of Telegram upload."""
    
    try:
        # Import aiohttp for HTTP requests
        import aiohttp
        
        api_url = f"https://api.telegram.org/bot{bot_token}"
        
        # First, send the video
        file_size = video_path.stat().st_size
        print(f"Uploading video to Telegram: {file_size / (1024*1024):.2f}MB")
        
        # Check file size limit (Telegram allows up to 2GB for bots)
        if file_size > 2 * 1024 * 1024 * 1024:
            print("Error: Video file exceeds Telegram's 2GB limit")
            return False, ""
            
        async with aiohttp.ClientSession() as session:
            # Prepare form data
            form = aiohttp.FormData()
            form.add_field('chat_id', chat_id)
            form.add_field('caption', caption, quote=False)
            form.add_field('parse_mode', 'Markdown', quote=False)
            
            with open(video_path, 'rb') as f:
                form.add_field('video', f, filename=video_path.name, content_type='video/mp4')
                
                async with session.post(f"{api_url}/sendVideo", data=form) as response:
                    result = await response.json()
                    
                    if result.get('ok'):
                        message_id = result['result']['message_id']
                        # Construct message link
                        # For channels: https://t.me/channel_name/message_id
                        # For groups: depends on chat type
                        message_link = f"https://t.me/c/{chat_id.lstrip('-')}/{message_id}" if chat_id.startswith('-') else f"https://t.me/{chat_id}/{message_id}"
                        print(f"Telegram upload successful! Message ID: {message_id}")
                        return True, message_link
                    else:
                        print(f"Telegram API error: {result}")
                        return False, ""
                        
    except ImportError:
        # Fallback to requests if aiohttp not available
        return _upload_sync(bot_token, chat_id, video_path, caption)
    except Exception as e:
        print(f"Telegram upload failed: {e}")
        return False, ""


def _upload_sync(bot_token: str, chat_id: str, video_path: Path, caption: str) -> tuple[bool, str]:
    """Synchronous fallback using requests library."""
    try:
        import requests
        
        api_url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
        files = {'video': open(video_path, 'rb')}
        data = {
            'chat_id': chat_id,
            'caption': caption,
            'parse_mode': 'Markdown'
        }
        
        response = requests.post(api_url, files=files, data=data, timeout=3600)
        result = response.json()
        
        if result.get('ok'):
            message_id = result['result']['message_id']
            message_link = f"https://t.me/c/{chat_id.lstrip('-')}/{message_id}" if chat_id.startswith('-') else f"https://t.me/{chat_id}/{message_id}"
            print(f"Telegram upload successful! Message ID: {message_id}")
            return True, message_link
        else:
            print(f"Telegram API error: {result}")
            return False, ""
            
    except Exception as e:
        print(f"Telegram upload failed: {e}")
        return False, ""
