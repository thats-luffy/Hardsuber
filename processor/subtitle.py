"""
Subtitle processing utilities.
Converts SRT to ASS with custom styling for FFmpeg.
"""

import re
from pathlib import Path
from datetime import timedelta


def parse_srt_time(time_str: str) -> timedelta:
    """Parse SRT timestamp format (HH:MM:SS,mmm) to timedelta."""
    time_str = time_str.strip()
    # Replace comma with dot for milliseconds
    time_str = time_str.replace(',', '.')
    
    try:
        parts = time_str.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds_parts = parts[2].split('.')
        seconds = int(seconds_parts[0])
        milliseconds = int(seconds_parts[1]) if len(seconds_parts) > 1 else 0
        
        return timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)
    except Exception as e:
        print(f"Error parsing SRT time '{time_str}': {e}")
        return timedelta(0)


def format_ass_time(td: timedelta) -> str:
    """Format timedelta to ASS timestamp format (H:MM:SS.cc)."""
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    centiseconds = int(td.microseconds / 10000)
    
    return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"


def convert_srt_to_ass(srt_path: Path, ass_path: Path, style: dict = None) -> bool:
    """Convert SRT file to ASS format with custom styling."""
    try:
        content = srt_path.read_text(encoding='utf-8')
        
        # Parse SRT entries
        entries = []
        blocks = re.split(r'\n\s*\n', content.strip())
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue
                
            # Skip index line
            idx = 0
            if lines[0].isdigit():
                idx = 1
                
            if idx + 2 >= len(lines):
                continue
                
            # Parse timing line
            timing_line = lines[idx]
            timing_match = re.match(r'(\d+:\d+:\d+[,\.]\d+)\s*-->\s*(\d+:\d+:\d+[,\.]\d+)', timing_line)
            if not timing_match:
                continue
                
            start_time = parse_srt_time(timing_match.group(1))
            end_time = parse_srt_time(timing_match.group(2))
            
            # Get text (may span multiple lines)
            text_lines = lines[idx + 1:]
            text = '\n'.join(text_lines)
            
            # Convert SRT tags to ASS tags
            text = text.replace('<i>', '{\\i1}').replace('</i>', '{\\i0}')
            text = text.replace('<b>', '{\\b1}').replace('</b>', '{\\b0}')
            text = text.replace('<u>', '{\\u1}').replace('</u>', '{\\u0}')
            
            entries.append({
                'start': start_time,
                'end': end_time,
                'text': text
            })
        
        if not entries:
            print("Warning: No subtitle entries found")
            return False
            
        # Generate ASS file
        ass_content = generate_ass_file(entries, style)
        ass_path.write_text(ass_content, encoding='utf-8')
        
        print(f"Converted {len(entries)} subtitle entries to ASS format")
        return True
        
    except Exception as e:
        print(f"Error converting SRT to ASS: {e}")
        return False


def generate_ass_style(settings: dict) -> dict:
    """Generate ASS style from settings."""
    
    def hex_to_ass(hex_color: str) -> str:
        """Convert hex color to ASS format (&HAABBGGRR)."""
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"&H{b:02X}{g:02X}{r:02X}"
    
    font_name = settings.get('fontFamily', 'Vazirmatn')
    font_size = settings.get('fontSize', 42)
    font_color = hex_to_ass(settings.get('fontColor', '#FFFFFF'))
    
    bold = 1 if settings.get('bold', False) else 0
    italic = 1 if settings.get('italic', False) else 0
    
    outline_width = settings.get('outlineWidth', 2) if settings.get('outlineEnabled', True) else 0
    shadow_depth = settings.get('shadowDepth', 2) if settings.get('shadowEnabled', True) else 0
    
    outline_color = hex_to_ass(settings.get('outlineColor', '#000000'))
    shadow_color = hex_to_ass(settings.get('shadowColor', '#000000'))
    
    # Background
    bg_enabled = settings.get('backgroundEnabled', True)
    bg_color = settings.get('backgroundColor', '#000000')
    bg_opacity = settings.get('backgroundOpacity', 60)
    # ASS alpha: 0 = opaque, 255 = transparent
    bg_alpha = int((100 - bg_opacity) / 100 * 255)
    bg_hex = hex_to_ass(bg_color)
    # Modify alpha channel in ASS color
    bg_ass = f"&H{bg_alpha:02X}{bg_hex[3:]}"
    
    # Margins
    h_padding = settings.get('horizontalPadding', 20)
    v_padding = settings.get('verticalPadding', 10)
    
    # Alignment
    position = settings.get('position', 'bottom')
    alignment = settings.get('alignment', 'center')
    
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
    ass_alignment = alignment_map.get((position, alignment), 2)
    
    return {
        'name': 'Default',
        'fontname': font_name,
        'fontsize': font_size,
        'primarycolor': font_color,
        'secondarycolor': font_color,
        'outlinecolor': outline_color,
        'backcolor': bg_ass if bg_enabled else '&H00000000',
        'bold': bold,
        'italic': italic,
        'borderstyle': 1,  # Outline and drop shadow
        'outline': outline_width,
        'shadow': shadow_depth,
        'alignment': ass_alignment,
        'marginl': h_padding,
        'marginr': h_padding,
        'marginv': v_padding,
        'encoding': 1  # Default charset
    }


def generate_ass_file(entries: list, style: dict = None) -> str:
    """Generate complete ASS file content."""
    
    if style is None:
        style = generate_ass_style({})
    
    # ASS header
    header = f"""[Script Info]
Title: Hardsub Subtitle
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
Timer: 100.0000

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: {style['name']},{style['fontname']},{style['fontsize']},{style['primarycolor']},{style['secondarycolor']},{style['outlinecolor']},{style['backcolor']},{style['bold']},{style['italic']},0,0,100,100,0,0,{style['borderstyle']},{style['outline']},{style['shadow']},{style['alignment']},{style['marginl']},{style['marginr']},{style['marginv']},{style['encoding']}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    
    # Dialogue entries
    dialogue_lines = []
    for entry in entries:
        start = format_ass_time(entry['start'])
        end = format_ass_time(entry['end'])
        text = entry['text'].replace('\n', '\\N')
        dialogue_lines.append(f"Dialogue: 0,{start},{end},{style['name']},,0,0,0,,{text}")
    
    return header + '\n'.join(dialogue_lines)
