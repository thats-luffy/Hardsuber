#!/usr/bin/env python3
"""
Validation utilities for Hardsub Platform
"""

import os
import subprocess
from pathlib import Path


def check_disk_space(min_bytes=5368709120):
    """
    Check if there's enough disk space available.
    Returns True if sufficient space, False otherwise.
    """
    try:
        # Get disk usage stats for root partition
        stat = os.statvfs('/')
        free_bytes = stat.f_bavail * stat.f_frsize
        
        print(f"Disk space - Free: {free_bytes / (1024**3):.2f} GB, Required: {min_bytes / (1024**3):.2f} GB")
        
        return free_bytes >= min_bytes
    except Exception as e:
        print(f"Failed to check disk space: {e}")
        return True  # Allow processing if we can't check


def validate_video(video_path):
    """
    Validate video file exists and is readable.
    Returns (success, error_message)
    """
    path = Path(video_path)
    
    if not path.exists():
        return False, "Video file does not exist"
    
    if not path.is_file():
        return False, "Video path is not a file"
    
    # Try to read first few bytes
    try:
        with open(path, 'rb') as f:
            header = f.read(12)
            if len(header) < 12:
                return False, "Video file is too small or unreadable"
    except IOError as e:
        return False, f"Cannot read video file: {e}"
    
    return True, ""


def validate_srt(srt_path):
    """
    Validate SRT subtitle file.
    Returns True if valid, False otherwise.
    """
    path = Path(srt_path)
    
    if not path.exists():
        print("SRT file does not exist")
        return False
    
    if not path.is_file():
        print("SRT path is not a file")
        return False
    
    try:
        content = path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        # Try other encodings
        try:
            content = path.read_text(encoding='latin-1')
        except Exception:
            print("SRT file encoding is invalid")
            return False
    except Exception as e:
        print(f"Cannot read SRT file: {e}")
        return False
    
    # Basic SRT validation
    lines = content.strip().split('\n')
    
    if len(lines) < 4:
        print("SRT file too short")
        return False
    
    # Check for at least one subtitle entry with timing
    has_timing = False
    for i, line in enumerate(lines):
        line = line.strip()
        if '-->' in line:
            has_timing = True
            break
    
    if not has_timing:
        print("SRT file has no valid timing entries")
        return False
    
    return True


def get_video_info_ffprobe(video_path):
    """
    Get video information using ffprobe.
    Returns dict with width, height, duration, codec, etc.
    """
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            str(video_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"FFprobe error: {result.stderr}")
            return None
        
        import json
        data = json.loads(result.stdout)
        
        # Find video stream
        video_stream = None
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'video':
                video_stream = stream
                break
        
        if not video_stream:
            print("No video stream found")
            return None
        
        format_info = data.get('format', {})
        
        return {
            'width': video_stream.get('width', 0),
            'height': video_stream.get('height', 0),
            'duration': float(format_info.get('duration', 0) or video_stream.get('duration', 0)),
            'codec': video_stream.get('codec_name', 'unknown'),
            'file_size': int(format_info.get('size', 0)),
            'bitrate': int(format_info.get('bit_rate', 0))
        }
        
    except subprocess.TimeoutExpired:
        print("FFprobe timed out")
        return None
    except Exception as e:
        print(f"FFprobe failed: {e}")
        return None
