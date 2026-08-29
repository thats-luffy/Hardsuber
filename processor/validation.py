"""
Validation utilities for video and subtitle files.
"""

import os
import subprocess
from pathlib import Path


def check_disk_space(path: Path, required_bytes: int) -> bool:
    """Check if there's enough disk space."""
    try:
        stat = os.statvfs(path)
        available = stat.f_bavail * stat.f_frsize
        return available >= required_bytes
    except Exception as e:
        print(f"Error checking disk space: {e}")
        return False


def get_video_info(video_path: Path) -> dict | None:
    """Get video information using ffprobe."""
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return None
            
        import json
        data = json.loads(result.stdout)
        
        video_stream = next((s for s in data.get('streams', []) if s.get('codec_type') == 'video'), None)
        format_info = data.get('format', {})
        
        return {
            'duration': float(format_info.get('duration', 0)),
            'size': int(format_info.get('size', 0)),
            'width': int(video_stream.get('width', 0)) if video_stream else 0,
            'height': int(video_stream.get('height', 0)) if video_stream else 0,
            'codec': video_stream.get('codec_name', '') if video_stream else '',
            'has_audio': any(s.get('codec_type') == 'audio' for s in data.get('streams', []))
        }
    except Exception as e:
        print(f"Error getting video info: {e}")
        return None


def validate_video(video_info: dict, max_size_mb: int, max_duration_minutes: int) -> bool:
    """Validate video file against limits."""
    size_mb = video_info['size'] / (1024 * 1024)
    duration_minutes = video_info['duration'] / 60
    
    print(f"Video info: {video_info['width']}x{video_info['height']}, {size_mb:.2f}MB, {duration_minutes:.2f}min")
    
    # Check size
    if size_mb > max_size_mb:
        print(f"خطا: حجم ویدیو بیشتر از حد مجاز {max_size_mb} مگابایت است. ({size_mb:.2f}MB)")
        return False
        
    # Check duration
    if duration_minutes > max_duration_minutes:
        print(f"خطا: مدت ویدیو بیشتر از {max_duration_minutes} دقیقه است. ({duration_minutes:.2f}min)")
        return False
        
    # Check resolution
    if video_info['width'] > 3840 or video_info['height'] > 2160:
        print(f"خطا: رزولوشن ویدیو بیشتر از 4K است. ({video_info['width']}x{video_info['height']})")
        return False
        
    return True


def validate_srt(srt_path: Path, max_size_mb: int) -> bool:
    """Validate SRT subtitle file."""
    try:
        if not srt_path.exists():
            print("خطا: فایل SRT وجود ندارد.")
            return False
            
        size_mb = srt_path.stat().st_size / (1024 * 1024)
        if size_mb > max_size_mb:
            print(f"خطا: حجم فایل زیرنویس بیشتر از {max_size_mb}MB است.")
            return False
            
        # Basic SRT validation - check for timing patterns
        content = srt_path.read_text(encoding='utf-8')
        if '-->' not in content:
            print("خطا: فایل SRT معتبر نیست (الگوی زمانی یافت نشد).")
            return False
            
        print(f"SRT validation passed: {size_mb:.2f}MB")
        return True
        
    except UnicodeDecodeError:
        print("خطا: فایل SRT باید UTF-8 باشد.")
        return False
    except Exception as e:
        print(f"خطا در اعتبارسنجی SRT: {e}")
        return False
