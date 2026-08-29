#!/usr/bin/env python3
"""
FFmpeg utilities for Hardsub Platform
Builds FFmpeg commands and parses progress output
"""

import re
from pathlib import Path


def get_video_info(probe_data):
    """
    Extract video information from ffprobe JSON output.
    Returns dict with width, height, duration, codec, etc.
    """
    # Find video stream
    video_stream = None
    for stream in probe_data.get('streams', []):
        if stream.get('codec_type') == 'video':
            video_stream = stream
            break
    
    if not video_stream:
        return {
            'width': 0,
            'height': 0,
            'duration': 0,
            'codec': 'unknown'
        }
    
    format_info = probe_data.get('format', {})
    
    # Calculate duration from format or stream
    duration = float(format_info.get('duration', 0) or 0)
    if duration <= 0:
        duration = float(video_stream.get('duration', 0) or 0)
    
    return {
        'width': video_stream.get('width', 0),
        'height': video_stream.get('height', 0),
        'duration': duration,
        'codec': video_stream.get('codec_name', 'unknown'),
        'file_size': int(format_info.get('size', 0)),
        'bitrate': int(format_info.get('bit_rate', 0))
    }


def parse_ffmpeg_progress(line, total_duration):
    """
    Parse FFmpeg progress output line.
    Returns dict with time info or None if not a progress line.
    """
    # Look for time= pattern in FFmpeg output
    # Example: frame= 1234 fps=25 q=28.0 size=   12345kB time=00:01:23.45 bitrate=1234.5kbits/s speed=1.23x
    
    time_match = re.search(r'time=(\d{2}):(\d{2}):(\d{2})\.(\d{2})', line)
    
    if time_match:
        hours = int(time_match.group(1))
        minutes = int(time_match.group(2))
        seconds = int(time_match.group(3))
        centiseconds = int(time_match.group(4))
        
        time_seconds = hours * 3600 + minutes * 60 + seconds + centiseconds / 100
        
        return {
            'time_string': f"{hours:02d}:{minutes:02d}:{seconds:02d}",
            'time_seconds': time_seconds,
            'progress_percent': (time_seconds / total_duration * 100) if total_duration > 0 else 0
        }
    
    return None


def build_ffmpeg_command(video_path, ass_path, output_path, fonts_dir=None):
    """
    Build FFmpeg command for hardsubbing with ASS subtitles.
    Uses libass filter for proper subtitle rendering with styling.
    """
    video_path = Path(video_path)
    ass_path = Path(ass_path)
    output_path = Path(output_path)
    
    # Base command
    cmd = [
        'ffmpeg',
        '-y',  # Overwrite output
        '-i', str(video_path),
        '-vf'
    ]
    
    # Build the libass filter with font directory
    # The libass filter handles all styling from the ASS file
    ass_filter = f"libass=filename='{ass_path}'"
    
    if fonts_dir and fonts_dir.exists():
        # Add font directory for libass to find custom fonts
        ass_filter = f"libass=filename='{ass_path}':fontsdir='{fonts_dir}'"
    
    cmd.append(ass_filter)
    
    # Output settings
    cmd.extend([
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',  # Quality: 18-28, lower is better quality
        '-c:a', 'aac',
        '-b:a', '192k',
        '-movflags', '+faststart',
        str(output_path)
    ])
    
    return cmd


def build_ffmpeg_command_with_overlay(video_path, ass_path, output_path, fonts_dir=None, 
                                       config=None):
    """
    Alternative FFmpeg command that uses overlay filter for background box.
    This provides more control over background rendering.
    """
    video_path = Path(video_path)
    ass_path = Path(ass_path)
    output_path = Path(output_path)
    
    # For complex background handling, we might need multiple filters
    # This is a more advanced approach
    
    cmd = [
        'ffmpeg',
        '-y',
        '-i', str(video_path),
        '-vf'
    ]
    
    # Use libass with additional options if config is provided
    ass_opts = []
    if fonts_dir and fonts_dir.exists():
        ass_opts.append(f"fontsdir='{fonts_dir}'")
    
    ass_filter = "libass=" + ':'.join([f"filename='{ass_path}'"] + ass_opts)
    cmd.append(ass_filter)
    
    cmd.extend([
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-movflags', '+faststart',
        str(output_path)
    ])
    
    return cmd


def estimate_output_size(input_size, crf=23):
    """
    Roughly estimate output file size based on input size and CRF.
    This is approximate - actual size depends on content complexity.
    """
    # CRF 23 typically results in similar or slightly smaller files
    # than the source for most content
    if crf < 20:
        multiplier = 1.2
    elif crf < 25:
        multiplier = 1.0
    else:
        multiplier = 0.8
    
    return int(input_size * multiplier)
