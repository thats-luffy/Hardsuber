"""
FFmpeg utilities for video processing.
"""

import subprocess
import re
from pathlib import Path


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


def build_ass_filter(settings: dict, font_path: Path | None) -> str:
    """Build FFmpeg ass filter with custom styling."""
    font_name = settings.get('fontFamily', 'Vazirmatn')
    font_size = settings.get('fontSize', 42)
    font_color = settings.get('fontColor', '#FFFFFF')
    
    # Convert hex color to ASS format (AABBGGRR)
    def hex_to_ass(hex_color):
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"&H{b:02X}{g:02X}{r:02X}"
    
    primary_color = hex_to_ass(font_color)
    
    # Build style string
    bold = '1' if settings.get('bold', False) else '0'
    italic = '1' if settings.get('italic', False) else '0'
    
    outline_color = hex_to_ass(settings.get('outlineColor', '#000000'))
    shadow_color = hex_to_ass(settings.get('shadowColor', '#000000'))
    
    outline_width = settings.get('outlineWidth', 2) if settings.get('outlineEnabled', True) else 0
    shadow_depth = settings.get('shadowDepth', 2) if settings.get('shadowEnabled', True) else 0
    
    # Background
    bg_enabled = settings.get('backgroundEnabled', True)
    bg_color = settings.get('backgroundColor', '#000000')
    bg_opacity = settings.get('backgroundOpacity', 60) / 100
    bg_hex = hex_to_ass(bg_color)
    # ASS alpha is inverted (00 = opaque, FF = transparent)
    bg_alpha = int((1 - bg_opacity) * 255)
    
    # Position
    position = settings.get('position', 'bottom')
    margin_v = settings.get('verticalMargin', 30)
    
    # Alignment: 7=top-left, 8=top-center, 9=top-right, 4=mid-left, 5=mid-center, 6=mid-right, 1=bottom-left, 2=bottom-center, 3=bottom-right
    alignment_map = {
        ('top', 'left'): 7,
        ('top', 'center'): 8,
        ('top', 'right'): 9,
        ('center', 'left'): 4,
        ('center', 'center'): 5,
        ('center', 'right'): 6,
        ('bottom', 'left'): 1,
        ('bottom', 'center'): 2,
        ('bottom', 'right'): 3
    }
    alignment = alignment_map.get((position, settings.get('alignment', 'center')), 2)
    
    # Build the style override string for the filter
    # Format: \\fnFontName\\fsSize\\cColor\\3cOutlineColor\\4cShadowColor\\bordOutlineWidth\\shadShadowDepth\\alphaAlpha\\pos(x,y)
    
    filter_parts = [
        f"ass={settings.get('subtitle_path', 'subtitle.ass')}",
    ]
    
    # If we have a fonts directory, specify it
    if font_path and font_path.parent.exists():
        filter_parts.insert(0, f"fontsdir={font_path.parent}")
    
    return ','.join(filter_parts)


def run_ffmpeg_with_progress(
    input_path: Path,
    subtitle_path: Path,
    output_path: Path,
    font_path: Path | None = None,
    settings: dict = None,
    progress_callback=None
) -> bool:
    """Run FFmpeg with progress reporting."""
    
    if settings is None:
        settings = {}
    
    # Get video duration for progress calculation
    video_info = get_video_info(input_path)
    if not video_info:
        print("Error: Could not get video info")
        return False
        
    total_duration = video_info['duration']
    has_audio = video_info.get('has_audio', True)
    
    # Build FFmpeg command
    cmd = [
        'ffmpeg',
        '-i', str(input_path),
        '-vf', f"ass={subtitle_path}:fontsdir={font_path.parent if font_path else '.'}",
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-movflags', '+faststart'
    ]
    
    # Copy audio if present
    if has_audio:
        cmd.extend(['-c:a', 'copy'])
    
    cmd.append(str(output_path))
    
    print(f"Running FFmpeg: {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        current_time = 0
        
        for line in process.stderr:
            # Parse FFmpeg progress output
            time_match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
            if time_match:
                hours = int(time_match.group(1))
                minutes = int(time_match.group(2))
                seconds = float(time_match.group(3))
                current_time = hours * 3600 + minutes * 60 + seconds
                
                if total_duration > 0:
                    progress = (current_time / total_duration) * 100
                    if progress_callback:
                        progress_callback(progress / 100)
                    print(f"Progress: {progress:.1f}% ({current_time:.1f}s / {total_duration:.1f}s)")
                    
        process.wait()
        
        if process.returncode != 0:
            print(f"FFmpeg failed with code {process.returncode}")
            return False
            
        # Verify output file exists
        if not output_path.exists():
            print("Error: Output file was not created")
            return False
            
        print(f"Output file size: {output_path.stat().st_size / (1024*1024):.2f}MB")
        return True
        
    except Exception as e:
        print(f"FFmpeg error: {e}")
        return False
