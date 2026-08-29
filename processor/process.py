#!/usr/bin/env python3
"""
Video Processing Pipeline for Hardsub Platform
Downloads video, validates, hardsubs subtitles, uploads to Telegram
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Import local modules
from validation import validate_video, validate_srt, check_disk_space
from ffmpeg_utils import build_ffmpeg_command, get_video_info, parse_ffmpeg_progress
from subtitle import convert_srt_to_ass, generate_ass_style
from telegram import upload_to_telegram

# Configuration from environment
JOB_ID = os.environ.get("JOB_ID", "unknown")
VIDEO_URL = os.environ.get("VIDEO_URL", "")
SRT_URL = os.environ.get("SRT_URL", "")
TITLE = os.environ.get("TITLE", "Untitled")
SUBTITLE_CONFIG_JSON = os.environ.get("SUBTITLE_CONFIG", "{}")
API_CALLBACK_URL = os.environ.get("API_CALLBACK_URL", "")
API_KEY = os.environ.get("API_KEY", "")

# Limits
MAX_VIDEO_SIZE_BYTES = int(os.environ.get("MAX_VIDEO_SIZE_BYTES", "1073741824"))  # 1GB
MAX_DURATION_SECONDS = int(os.environ.get("MAX_DURATION_SECONDS", "1800"))  # 30 minutes
MAX_RESOLUTION = int(os.environ.get("MAX_RESOLUTION", "3840"))  # 4K
MIN_DISK_SPACE_BYTES = int(os.environ.get("MIN_DISK_SPACE_BYTES", "5368709120"))  # 5GB free space required

# Paths
WORK_DIR = Path(tempfile.mkdtemp(prefix=f"hardsub_{JOB_ID}_"))
FONTS_DIR = Path(__file__).parent.parent / "fonts"
OUTPUT_FILE = WORK_DIR / "output.mp4"

# Subtitle config
try:
    SUBTITLE_CONFIG = json.loads(SUBTITLE_CONFIG_JSON)
except json.JSONDecodeError:
    SUBTITLE_CONFIG = {}


def log(message):
    """Log message with timestamp"""
    timestamp = datetime.utcnow().isoformat() + "Z"
    print(f"[{timestamp}] {message}", flush=True)


def update_status(status, stage=None, progress=None, error=None):
    """Update job status via API callback"""
    if not API_CALLBACK_URL or not API_KEY:
        log(f"Status update skipped (no callback): {status}")
        return
    
    data = {"status": status}
    if stage:
        data["current_stage"] = stage
    if progress is not None:
        data["progress"] = progress
    if error:
        data["error"] = error[:500]  # Limit error message length
    
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
            log(f"Status updated: {status}")
    except Exception as e:
        log(f"Failed to update status: {e}")


def download_file(url, destination, max_size=None):
    """Download file with size limit"""
    import urllib.request
    
    log(f"Downloading: {url}")
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'HardsubBot/1.0'})
        
        with urllib.request.urlopen(req, timeout=300) as response:
            # Check Content-Length if available
            content_length = response.headers.get('Content-Length')
            if content_length and max_size:
                content_length = int(content_length)
                if content_length > max_size:
                    raise ValueError(f"File too large: {content_length} bytes (max: {max_size})")
            
            # Download with size tracking
            downloaded = 0
            chunk_size = 8192
            
            with open(destination, 'wb') as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    
                    downloaded += len(chunk)
                    if max_size and downloaded > max_size:
                        raise ValueError(f"Download exceeded size limit: {downloaded} bytes")
                    
                    f.write(chunk)
                    
                    # Progress reporting
                    if content_length:
                        progress = min(100, int((downloaded / content_length) * 100))
                        log(f"Download progress: {progress}%")
            
            log(f"Download complete: {destination} ({downloaded} bytes)")
            return downloaded
            
    except Exception as e:
        log(f"Download failed: {e}")
        raise


def run_ffprobe(video_path):
    """Run ffprobe to get video information"""
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
        raise RuntimeError(f"FFprobe failed: {result.stderr}")
    
    return json.loads(result.stdout)


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
    return True


def cleanup():
    """Clean up temporary files"""
    log(f"Cleaning up temporary directory: {WORK_DIR}")
    try:
        shutil.rmtree(WORK_DIR, ignore_errors=True)
    except Exception as e:
        log(f"Cleanup warning: {e}")


def main():
    """Main processing pipeline"""
    log(f"=== Starting Job: {JOB_ID} ===")
    log(f"Title: {TITLE}")
    log(f"Video URL: {VIDEO_URL}")
    log(f"SRT URL: {SRT_URL}")
    
    video_path = None
    srt_path = None
    
    try:
        # Step 1: Check system resources
        update_status("PROCESSING", "Checking system resources")
        if not check_disk_space(MIN_DISK_SPACE_BYTES):
            raise RuntimeError("Insufficient disk space")
        
        # Log system info
        subprocess.run(['df', '-h'], check=False)
        subprocess.run(['free', '-h'], check=False)
        subprocess.run(['nproc'], check=False)
        
        # Step 2: Prepare fonts
        update_status("PROCESSING", "Preparing fonts")
        prepare_fonts()
        
        # Step 3: Download video
        update_status("DOWNLOADING", "Downloading video", 0)
        video_path = WORK_DIR / "input.mp4"
        download_file(VIDEO_URL, video_path, max_size=MAX_VIDEO_SIZE_BYTES)
        update_status("DOWNLOADING", "Video downloaded", 100)
        
        # Step 4: Validate video with ffprobe
        update_status("PROCESSING", "Validating video")
        probe_data = run_ffprobe(video_path)
        video_info = get_video_info(probe_data)
        
        log(f"Video info: {video_info}")
        
        # Check duration
        if video_info['duration'] > MAX_DURATION_SECONDS:
            raise ValueError(f"Video too long: {video_info['duration']}s (max: {MAX_DURATION_SECONDS}s)")
        
        # Check resolution
        if video_info['width'] > MAX_RESOLUTION or video_info['height'] > MAX_RESOLUTION:
            raise ValueError(f"Video resolution too high: {video_info['width']}x{video_info['height']} (max: {MAX_RESOLUTION})")
        
        # Step 5: Download SRT
        update_status("DOWNLOADING", "Downloading subtitle")
        srt_path = WORK_DIR / "subtitle.srt"
        download_file(SRT_URL, srt_path, max_size=10 * 1024 * 1024)  # 10MB limit for SRT
        
        # Step 6: Validate SRT
        update_status("PROCESSING", "Validating subtitle")
        if not validate_srt(srt_path):
            raise ValueError("Invalid SRT file")
        
        # Step 7: Convert SRT to ASS with styling
        update_status("PROCESSING", "Generating subtitle styles")
        ass_path = WORK_DIR / "subtitle.ass"
        ass_content = convert_srt_to_ass(srt_path, SUBTITLE_CONFIG, FONTS_DIR)
        
        with open(ass_path, 'w', encoding='utf-8') as f:
            f.write(ass_content)
        
        log(f"ASS file created: {ass_path}")
        
        # Step 8: Run FFmpeg hardsub
        update_status("PROCESSING", "Hardsubbing video", 0)
        
        ffmpeg_cmd = build_ffmpeg_command(
            video_path=video_path,
            ass_path=ass_path,
            output_path=OUTPUT_FILE,
            fonts_dir=FONTS_DIR
        )
        
        log(f"Running FFmpeg: {' '.join(ffmpeg_cmd)}")
        
        # Run FFmpeg with progress parsing
        process = subprocess.Popen(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE
        )
        
        total_duration = video_info['duration']
        
        # Read stderr for progress
        ffmpeg_progress = ""
        while True:
            line = process.stderr.readline()
            if not line:
                break
            
            line_str = line.decode('utf-8', errors='ignore')
            ffmpeg_progress += line_str
            
            # Parse progress
            progress_data = parse_ffmpeg_progress(line_str, total_duration)
            if progress_data and total_duration > 0:
                current_time = progress_data.get('time_seconds', 0)
                progress_pct = min(95, int((current_time / total_duration) * 100))
                update_status("PROCESSING", "Hardsubbing", progress_pct)
        
        process.wait()
        
        if process.returncode != 0:
            stderr_output = process.stderr.read().decode('utf-8', errors='ignore')
            raise RuntimeError(f"FFmpeg failed: {stderr_output[:500]}")
        
        log(f"FFmpeg completed successfully")
        update_status("PROCESSING", "Hardsubbing complete", 100)
        
        # Verify output exists
        if not OUTPUT_FILE.exists():
            raise RuntimeError("Output file was not created")
        
        output_size = OUTPUT_FILE.stat().st_size
        log(f"Output file size: {output_size} bytes")
        
        # Step 9: Upload to Telegram
        update_status("UPLOADING", "Uploading to Telegram", 0)
        
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
                error=None
            )
            
            # Update with Telegram info (if callback supports it)
            if API_CALLBACK_URL and API_KEY:
                try:
                    import urllib.request
                    data = {
                        "telegram_message_id": telegram_result.get('message_id'),
                        "telegram_message_link": telegram_result.get('message_link')
                    }
                    req = urllib.request.Request(
                        API_CALLBACK_URL,
                        data=json.dumps(data).encode('utf-8'),
                        headers={
                            'Content-Type': 'application/json',
                            'X-API-Key': API_KEY
                        },
                        method='POST'
                    )
                    urllib.request.urlopen(req, timeout=10)
                except Exception as e:
                    log(f"Failed to update Telegram info: {e}")
        else:
            log(f"Telegram upload failed: {telegram_result.get('error', 'Unknown error')}")
            # Still mark as completed since hardsub succeeded
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
