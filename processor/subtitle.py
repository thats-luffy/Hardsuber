#!/usr/bin/env python3
"""
Subtitle processing utilities for Hardsub Platform
Converts SRT to ASS with full styling support for Persian/RTL
"""

import re
from pathlib import Path
from datetime import timedelta


def parse_srt(srt_path):
    """
    Parse SRT file and return list of subtitle entries.
    Each entry: {index, start, end, text}
    """
    content = srt_path.read_text(encoding='utf-8')
    
    # Normalize line endings
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    
    entries = []
    blocks = re.split(r'\n\n+', content.strip())
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue
        
        try:
            index = int(lines[0].strip())
        except ValueError:
            continue
        
        # Parse timing line
        timing_line = lines[1].strip()
        timing_match = re.match(
            r'(\d{2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2})[,.](\d{3})',
            timing_line
        )
        
        if not timing_match:
            continue
        
        # Convert to milliseconds
        h1, m1, s1, ms1 = map(int, timing_match.groups()[:4])
        h2, m2, s2, ms2 = map(int, timing_match.groups()[4:])
        
        start_ms = h1 * 3600000 + m1 * 60000 + s1 * 1000 + ms1
        end_ms = h2 * 3600000 + m2 * 60000 + s2 * 1000 + ms2
        
        # Join remaining lines as text
        text = '\n'.join(lines[2:])
        
        entries.append({
            'index': index,
            'start_ms': start_ms,
            'end_ms': end_ms,
            'text': text
        })
    
    return entries


def format_ass_time(ms):
    """
    Format milliseconds as ASS time: H:MM:SS.cc
    """
    hours = ms // 3600000
    minutes = (ms % 3600000) // 60000
    seconds = (ms % 60000) // 1000
    centiseconds = (ms % 1000) // 10
    
    return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"


def hex_to_ass_color(hex_color):
    """
    Convert hex color (#RRGGBB) to ASS color (&HBBGGRR&).
    ASS uses BGR order and requires &H prefix/suffix.
    """
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"&H{b:02X}{g:02X}{r:02X}&"
    return "&HFFFFFF&"  # Default white


def hex_to_ass_color_with_alpha(hex_color, opacity_percent):
    """
    Convert hex color with opacity to ASS color with alpha.
    Alpha in ASS is inverted: 00 = opaque, FF = transparent
    """
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Calculate alpha (inverted: 0% opacity = FF alpha, 100% opacity = 00 alpha)
        alpha = int(255 * (100 - opacity_percent) / 100)
        
        return f"&H{alpha:02X}{b:02X}{g:02X}{r:02X}&"
    return "&H00FFFFFF&"  # Default opaque white


def generate_ass_style(config, fonts_dir):
    """
    Generate ASS style line from configuration.
    Returns the [V4+ Styles] section content.
    """
    # Extract config values with defaults
    font_family = config.get('fontFamily', 'Vazirmatn')
    font_size = config.get('fontSize', 42)
    bold = config.get('bold', False)
    italic = config.get('italic', False)
    font_color = config.get('fontColor', '#FFFFFF')
    
    outline_enabled = config.get('outlineEnabled', True)
    outline_color = config.get('outlineColor', '#000000')
    outline_width = config.get('outlineWidth', 2)
    
    shadow_enabled = config.get('shadowEnabled', True)
    shadow_color = config.get('shadowColor', '#000000')
    shadow_depth = config.get('shadowDepth', 2)
    
    background_enabled = config.get('backgroundEnabled', True)
    background_color = config.get('backgroundColor', '#000000')
    background_opacity = config.get('backgroundOpacity', 60)
    
    position = config.get('position', 'bottom')
    vertical_margin = config.get('verticalMargin', 30)
    alignment = config.get('alignment', 'center')
    
    horizontal_padding = config.get('horizontalPadding', 20)
    vertical_padding = config.get('verticalPadding', 10)
    
    # Map font weight
    weight = 700 if bold else 400
    
    # Map alignment for ASS
    # ASS alignments: 1=Bottom Left, 2=Bottom Center, 3=Bottom Right
    #                 4=Middle Left, 5=Middle Center, 6=Middle Right
    #                 7=Top Left, 8=Top Center, 9=Top Right
    if position == 'top':
        base_align = 7  # Top
    elif position == 'center':
        base_align = 4  # Middle
    else:  # bottom
        base_align = 1  # Bottom
    
    if alignment == 'left':
        ass_alignment = base_align
    elif alignment == 'right':
        ass_alignment = base_align + 2
    else:  # center
        ass_alignment = base_align + 1
    
    # For background box, we use BorderStyle=3 (opaque box)
    # This creates a solid background behind the text
    border_style = 3 if background_enabled else 1
    
    # Convert colors
    primary_color = hex_to_ass_color(font_color)
    outline_color_ass = hex_to_ass_color(outline_color)
    shadow_color_ass = hex_to_ass_color(shadow_color)
    
    # Background color with opacity (only used if BorderStyle=3)
    bg_color_ass = hex_to_ass_color_with_alpha(background_color, background_opacity)
    
    # Build style line
    # Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,
    #         Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,
    #         Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
    
    # The back colour is used for the background box when BorderStyle=3
    style_line = (
        f"Default,"                          # Name
        f"{font_family},"                    # Fontname
        f"{font_size},"                      # Fontsize
        f"{primary_color},"                  # PrimaryColour
        f"{primary_color},"                  # SecondaryColour (same as primary)
        f"{outline_color_ass},"              # OutlineColour
        f"{bg_color_ass},"                   # BackColour (background with alpha)
        f"{weight},"                         # Bold (400 or 700)
        f"{1 if italic else 0},"             # Italic
        "0,"                                 # Underline
        "0,"                                 # StrikeOut
        "100,"                               # ScaleX
        "100,"                               # ScaleY
        "0,"                                 # Spacing
        "0,"                                 # Angle
        f"{border_style},"                   # BorderStyle (1=outline, 3=opaque box)
        f"{outline_width if outline_enabled else 0},"  # Outline
        f"{shadow_depth if shadow_enabled else 0},"    # Shadow
        f"{ass_alignment},"                  # Alignment
        f"{horizontal_padding},"             # MarginL (also affects background padding)
        f"{horizontal_padding},"             # MarginR
        f"{vertical_margin},"                # MarginV (vertical position)
        "1"                                  # Encoding (1=Default, supports Unicode)
    )
    
    return style_line


def convert_srt_to_ass(srt_path, config, fonts_dir):
    """
    Convert SRT file to ASS format with custom styling.
    Returns the complete ASS file content as string.
    """
    entries = parse_srt(srt_path)
    
    if not entries:
        # Return minimal valid ASS even if no entries
        return create_empty_ass(config, fonts_dir)
    
    style_line = generate_ass_style(config, fonts_dir)
    
    # Build ASS content
    ass_lines = [
        "[Script Info]",
        "; Script generated by Hardsub Platform",
        "ScriptType: v4.00+",
        "PlayResX: 1920",
        "PlayResY: 1080",
        "Timer: 100.0000",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: {style_line}",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    
    # Add each subtitle entry
    for entry in entries:
        # Escape special ASS characters in text
        # { } are used for tags, \N for line breaks
        text = entry['text']
        text = text.replace('\\', '\\\\')
        text = text.replace('{', '\\{')
        text = text.replace('}', '\\}')
        
        # Convert newlines to ASS line breaks
        text = text.replace('\n', '\\N')
        
        start_time = format_ass_time(entry['start_ms'])
        end_time = format_ass_time(entry['end_ms'])
        
        ass_lines.append(
            f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{text}"
        )
    
    return '\n'.join(ass_lines)


def create_empty_ass(config, fonts_dir):
    """Create a minimal valid ASS file with just the header and styles."""
    style_line = generate_ass_style(config, fonts_dir)
    
    return '\n'.join([
        "[Script Info]",
        "; Script generated by Hardsub Platform",
        "ScriptType: v4.00+",
        "PlayResX: 1920",
        "PlayResY: 1080",
        "Timer: 100.0000",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: {style_line}",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ])
