#!/usr/bin/env python3
"""
Video Processing Pipeline for Hardsub Platform
Receives already-downloaded files from GitHub Actions workflow
Performs hardsubbing and Telegram upload
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import threading

# Import local modules
from validation import validate_video, validate_srt, check_disk_space
from ffmpeg_utils import build_ffmpeg_command, get_video_info, parse_ffmpeg_progress
from subtitle import convert_srt_to_ass, generate_ass_style
from telegram import upload_to_telegram

# Configuration from environment - passed from GitHub Actions workflow
JOB_ID = os.environ.get("JOB_ID", "unknown")
TITLE = os.environ.get("TITLE", "Untitled")
SUBTITLE_CONFIG_JSON = os.environ.get("SUBTITLE_CONFIG", "{}")
API_CALLBACK_URL = os.environ.get("API_CALLBACK_URL", "")
API_KEY = os.environ.get("API_KEY", "")

# File paths - already downloaded by workflow
WORK_DIR = Path(os.environ.get("WORK_DIR", ""))
VIDEO_FILE = Path(os.environ.get("VIDEO_FILE", ""))
SRT_FILE = Path(os.environ.get("SRT_FILE", ""))

# Video metadata - already validated by workflow
VIDEO_DURATION = float(os.environ.get("VIDEO_DURATION", "0"))
VIDEO_WIDTH = int(os.environ.get("VIDEO_WIDTH", "0"))
VIDEO_HEIGHT = int(os.environ.get("VIDEO_HEIGHT", "0"))
VIDEO_SIZE = int(os.environ.get("VIDEO_SIZE", "0"))

# Limits
MAX_RESOLUTION = int(os.environ.get("MAX_RESOLUTION", "3840"))  # 4K
MIN_DISK_SPACE_BYTES = int(os.environ.get("MIN_DISK_SPACE_BYTES", "5368709120"))  # 5GB free space required

# Paths
FONTS_DIR = Path(__file__).parent.parent / "fonts"
OUTPUT_FILE = WORK_DIR / "output.mp4" if WORK_DIR else Path(tempfile.mktemp(suffix=".mp4"))

# Subtitle config
try:
    SUBTITLE_CONFIG = json.loads(SUBTITLE_CONFIG_JSON)
except json.JSONDecodeError:
    SUBTITLE_CONFIG = {}


def log(message):
    """Log message with timestamp"""
    timestamp = datetime.utcnow().isoformat() + "Z"
    print(f"[{timestamp}] {message}", flush=True)


def update_status(status, stage=None, progress=None, error=None, **extra_data):
    """Update job status via API callback"""
    if not API_CALLBACK_URL or not API_KEY:
        log(f"Status update skipped (no callback): {status}")
        return
    
    data = {"status": status}
    if stage:
        data["current_stage"] = stage
    if progress is not None:
        data["progress"] = min(100, max(0, int(progress)))
    if error:
        data["error"] = error[:500]  # Limit error message length
    
    # Add any extra data (telegram info, etc.)
    for key, value in extra_data.items():
        if value is not None:
            data[key] = value
    
    try:
        import urllib.request
        req = urllib.request.Request(
            API_CALLBACK_URL,
            data=json.dumps(data).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'X-API-Key': API_KEY
            },
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            log(f"Status updated: {status} (progress: {progress}%)")
    except Exception as e:
        log(f"Failed to update status: {e}")


def prepare_fonts():
    """Ensure fonts are available"""
    log(f"Checking fonts in: {FONTS_DIR}")
    
    if not FONTS_DIR.exists():
        log("Warning: Fonts directory does not exist")
        return False
    
    font_files = list(FONTS_DIR.glob("*.ttf")) + list(FONTS_DIR.glob("*.otf"))
    if not font_files:
        log("Warning: No font files found")
        return False
    
    log(f"Found {len(font_files)} font files")
    for f in font_files:
        log(f"  - {f.name}")
    return True


def cleanup():
    """Clean up temporary files"""
    if WORK_DIR and WORK_DIR.exists():
        log(f"Cleaning up temporary directory: {WORK_DIR}")
        try:
            shutil.rmtree(WORK_DIR, ignore_errors=True)
        except Exception as e:
            log(f"Cleanup warning: {e}")


def main():
    """Main processing pipeline"""
    log(f"=== Starting Job: {JOB_ID} ===")
    log(f"Title: {TITLE}")
    log(f"Video file: {VIDEO_FILE}")
    log(f"Subtitle file: {SRT_FILE}")
    log(f"Video duration: {VIDEO_DURATION}s, Resolution: {VIDEO_WIDTH}x{VIDEO_HEIGHT}")
    
    try:
        # Step 1: Check system resources
        update_status("PROCESSING", "Checking system resources", 5)
        if not check_disk_space(MIN_DISK_SPACE_BYTES):
            raise RuntimeError("Insufficient disk space")
        
        # Step 2: Prepare fonts
        update_status("PROCESSING", "Preparing fonts", 15)
        if not prepare_fonts():
            log("Warning: Font preparation failed, continuing with system fonts")
        
        # Step 3: Validate video file exists (already downloaded by workflow)
        update_status("PROCESSING", "Validating video file", 20)
        if not VIDEO_FILE.exists():
            raise RuntimeError(f"Video file not found: {VIDEO_FILE}")
        
        video_size = VIDEO_FILE.stat().st_size
        log(f"Video file size: {video_size} bytes")
        
        # Step 4: Validate SRT file exists (already downloaded by workflow)
        update_status("PROCESSING", "Validating subtitle file", 25)
        if not SRT_FILE.exists():
            raise RuntimeError(f"Subtitle file not found: {SRT_FILE}")
        
        if not validate_srt(SRT_FILE):
            raise ValueError("Invalid SRT file")
        
        # Step 5: Convert SRT to ASS with styling
        update_status("PROCESSING", "Generating subtitle styles", 30)
        ass_path = WORK_DIR / "subtitle.ass" if WORK_DIR else Path(tempfile.mktemp(suffix=".ass"))
        ass_content = convert_srt_to_ass(SRT_FILE, SUBTITLE_CONFIG, FONTS_DIR)
        
        with open(ass_path, 'w', encoding='utf-8') as f:
            f.write(ass_content)
        
        log(f"ASS file created: {ass_path}")
        
        # Step 6: Run FFmpeg hardsub with progress tracking
        update_status("HARDSUBBING", "Starting FFmpeg", 30)
        
        ffmpeg_cmd = build_ffmpeg_command(
            video_path=VIDEO_FILE,
            ass_path=ass_path,
            output_path=OUTPUT_FILE,
            fonts_dir=FONTS_DIR
        )
        
        log(f"Running FFmpeg command")
        
        # Run FFmpeg with progress output using -progress pipe:1
        progress_cmd = ffmpeg_cmd.copy()
        progress_cmd.insert(1, '-nostats')
        progress_cmd.insert(1, '-progress', 'pipe:1')
        
        process = subprocess.Popen(
            progress_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            bufsize=1
        )
        
        total_duration = VIDEO_DURATION
        current_progress_seconds = 0
        
        # Read stdout for progress (machine-readable format)
        def read_progress():
            nonlocal current_progress_seconds
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                try:
                    line_str = line.decode('utf-8', errors='ignore').strip()
                    if line_str.startswith('out_time_ms='):
                        time_ms = int(line_str.split('=')[1])
                        current_progress_seconds = time_ms / 1_000_000
                        if total_duration > 0:
                            progress_pct = 30 + (current_progress_seconds / total_duration * 65)  # 30-95%
                            update_status("HARDSUBBING", f"Hardsubbing: {current_progress_seconds:.1f}s/{total_duration:.1f}s", progress_pct)
                except Exception:
                    pass
        
        # Read stderr for errors
        stderr_output = []
        def read_stderr():
            while True:
                line = process.stderr.readline()
                if not line:
                    break
                stderr_output.append(line.decode('utf-8', errors='ignore'))
        
        # Start threads for reading output
        stdout_thread = threading.Thread(target=read_progress)
        stderr_thread = threading.Thread(target=read_stderr)
        
        stdout_thread.start()
        stderr_thread.start()
        
        # Wait for process to complete
        process.wait()
        stdout_thread.join()
        stderr_thread.join()
        
        if process.returncode != 0:
            error_msg = ''.join(stderr_output)[-500:]
            raise RuntimeError(f"FFmpeg failed with code {process.returncode}: {error_msg}")
        
        log(f"FFmpeg completed successfully")
        update_status("PROCESSING", "Hardsubbing complete", 95)
        
        # Verify output exists
        if not OUTPUT_FILE.exists():
            raise RuntimeError("Output file was not created")
        
        output_size = OUTPUT_FILE.stat().st_size
        log(f"Output file size: {output_size} bytes")
        
        # Step 7: Upload to Telegram
        update_status("UPLOADING", "Uploading to Telegram", 95)
        
        video_info = {
            'width': VIDEO_WIDTH,
            'height': VIDEO_HEIGHT,
            'duration': VIDEO_DURATION
        }
        
        telegram_result = upload_to_telegram(
            video_path=OUTPUT_FILE,
            title=TITLE,
            job_id=JOB_ID,
            subtitle_config=SUBTITLE_CONFIG,
            video_info=video_info
        )
        
        if telegram_result.get('success'):
            log(f"Telegram upload successful: {telegram_result.get('message_link', 'N/A')}")
            update_status(
                "COMPLETED",
                "Upload complete",
                100,
                error=None,
                telegram_message_id=telegram_result.get('message_id'),
                telegram_message_link=telegram_result.get('message_link')
            )
        else:
            log(f"Telegram upload failed: {telegram_result.get('error', 'Unknown error')}")
            update_status(
                "COMPLETED",
                "Hardsub complete (Telegram upload failed)",
                100,
                error=telegram_result.get('error', 'Telegram upload failed')
            )
        
        log(f"=== Job {JOB_ID} Completed Successfully ===")
        
    except Exception as e:
        error_msg = str(e)[:500]
        log(f"=== Job {JOB_ID} Failed: {error_msg} ===")
        update_status("FAILED", "Error", error=error_msg)
        
    finally:
        # Always cleanup
        cleanup()


if __name__ == '__main__':
    main()
