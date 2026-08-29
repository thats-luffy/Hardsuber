#!/usr/bin/env python3
"""
Main processor for hardsub video processing.
This script is called by GitHub Actions workflow.
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
from pathlib import Path

# Import local modules
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from validation import validate_video, validate_srt, check_disk_space
from ffmpeg_utils import get_video_info, run_ffmpeg_with_progress
from telegram import upload_to_telegram
from subtitle import convert_srt_to_ass, generate_ass_style


class HardsubProcessor:
    def __init__(self, job_id: str, video_url: str, srt_url: str, title: str, settings: dict):
        self.job_id = job_id
        self.video_url = video_url
        self.srt_url = srt_url
        self.title = title
        self.settings = settings
        
        # Create temporary working directory
        self.work_dir = Path(tempfile.mkdtemp(prefix=f'hardsub_{job_id}_'))
        self.video_path = self.work_dir / 'input.mp4'
        self.srt_path = self.work_dir / 'subtitle.srt'
        self.ass_path = self.work_dir / 'subtitle.ass'
        self.output_path = self.work_dir / 'output.mp4'
        self.fonts_dir = self.work_dir / 'fonts'
        
        # Configuration
        self.max_video_size_mb = int(os.environ.get('MAX_VIDEO_SIZE_MB', 1024))
        self.max_duration_minutes = int(os.environ.get('MAX_DURATION_MINUTES', 30))
        self.max_srt_size_mb = int(os.environ.get('MAX_SRT_SIZE_MB', 10))
        
    def log(self, message: str):
        """Log message with job ID prefix."""
        print(f"[{self.job_id}] {message}", flush=True)
        
    def progress(self, stage: str, percent: int):
        """Report progress to GitHub Actions output."""
        print(f"::notice::STAGE={stage},PROGRESS={percent}", flush=True)
        
    def cleanup(self):
        """Clean up temporary files."""
        self.log("Cleaning up temporary files...")
        try:
            shutil.rmtree(self.work_dir, ignore_errors=True)
            self.log("Cleanup completed.")
        except Exception as e:
            self.log(f"Warning: Cleanup failed: {e}")
            
    def download_file(self, url: str, destination: Path) -> bool:
        """Download a file from URL."""
        self.log(f"Downloading {url} to {destination}")
        try:
            result = subprocess.run(
                ['curl', '-L', '-o', str(destination), url],
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            if result.returncode != 0:
                self.log(f"Download failed: {result.stderr}")
                return False
            self.log(f"Download completed: {destination.stat().st_size} bytes")
            return True
        except Exception as e:
            self.log(f"Download error: {e}")
            return False
            
    def prepare_fonts(self):
        """Prepare fonts for FFmpeg."""
        self.log("Preparing fonts...")
        self.fonts_dir.mkdir(exist_ok=True)
        
        # Copy fonts from repository fonts directory
        repo_fonts = Path(__file__).parent.parent / 'fonts'
        if repo_fonts.exists():
            for font_file in repo_fonts.glob('*.ttf'):
                dest = self.fonts_dir / font_file.name
                shutil.copy2(font_file, dest)
                self.log(f"Copied font: {font_file.name}")
        else:
            self.log("Warning: Fonts directory not found, using system fonts")
            
        return True
        
    def validate_inputs(self) -> bool:
        """Validate video and subtitle files."""
        self.progress('validating', 0)
        
        # Check disk space
        if not check_disk_space(self.work_dir, self.max_video_size_mb * 2 * 1024 * 1024):
            self.log("خطا: فضای کافی برای پردازش وجود ندارد.")
            return False
            
        # Validate video
        self.log("Validating video file...")
        video_info = get_video_info(self.video_path)
        if not video_info:
            self.log("خطا: نمی‌توان اطلاعات ویدیو را خواند.")
            return False
            
        if not validate_video(video_info, self.max_video_size_mb, self.max_duration_minutes):
            return False
            
        # Validate SRT
        self.log("Validating subtitle file...")
        if not validate_srt(self.srt_path, self.max_srt_size_mb):
            return False
            
        self.progress('validating', 100)
        return True
        
    def convert_subtitle(self) -> bool:
        """Convert SRT to ASS with custom styling."""
        self.log("Converting SRT to ASS with custom styling...")
        self.progress('converting_subtitles', 15)
        
        try:
            style = generate_ass_style(self.settings)
            if convert_srt_to_ass(self.srt_path, self.ass_path, style):
                self.log("Subtitle conversion completed.")
                return True
            else:
                self.log("خطا: تبدیل زیرنویس ناموفق بود.")
                return False
        except Exception as e:
            self.log(f"خطا: {e}")
            return False
            
    def process_video(self) -> bool:
        """Run FFmpeg to hardsub the video."""
        self.log("Starting FFmpeg processing...")
        self.progress('hardsubbing', 20)
        
        # Build FFmpeg command
        video_info = get_video_info(self.video_path)
        if not video_info:
            return False
            
        # Get font path
        font_name = self.settings.get('fontFamily', 'Vazirmatn')
        font_path = self.fonts_dir / f'{font_name}-Regular.ttf'
        
        # If specific font not found, use any Vazirmatn font
        if not font_path.exists():
            font_path = list(self.fonts_dir.glob('Vazirmatn*.ttf'))[0] if list(self.fonts_dir.glob('Vazirmatn*.ttf')) else None
            
        if font_path:
            self.log(f"Using font: {font_path}")
        else:
            self.log("Warning: No Vazirmatn font found, using default")
            
        success = run_ffmpeg_with_progress(
            input_path=self.video_path,
            subtitle_path=self.ass_path,
            output_path=self.output_path,
            font_path=font_path,
            settings=self.settings,
            progress_callback=lambda p: self.progress('hardsubbing', 20 + int(p * 60))
        )
        
        if success:
            self.log("FFmpeg processing completed.")
            self.progress('hardsubbing', 80)
        else:
            self.log("خطا: پردازش FFmpeg ناموفق بود.")
            
        return success
        
    def upload_telegram(self) -> tuple[bool, str]:
        """Upload processed video to Telegram."""
        self.log("Uploading to Telegram...")
        self.progress('uploading', 85)
        
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            self.log("Warning: Telegram credentials not configured, skipping upload.")
            return True, ""
            
        caption = f"""🎬 {self.title}

🆔 Job: {self.job_id}

✅ Hardsub completed
🔤 Font: {self.settings.get('fontFamily', 'Vazirmatn')}
📐 Resolution: {self.settings.get('resolution', '1920x1080')}
"""
        
        success, link = upload_to_telegram(
            bot_token=bot_token,
            chat_id=chat_id,
            video_path=self.output_path,
            caption=caption
        )
        
        if success:
            self.log(f"Telegram upload completed: {link}")
            self.progress('uploading', 100)
        else:
            self.log("خطا: آپلود به تلگرام ناموفق بود.")
            
        return success, link
        
    def run(self) -> bool:
        """Run the complete processing pipeline."""
        self.log(f"Starting processing for job: {self.job_id}")
        self.log(f"Title: {self.title}")
        self.log(f"Video URL: {self.video_url}")
        self.log(f"SRT URL: {self.srt_url}")
        
        try:
            # Download video
            self.progress('downloading', 5)
            if not self.download_file(self.video_url, self.video_path):
                raise Exception("Failed to download video")
                
            # Download SRT
            if not self.download_file(self.srt_url, self.srt_path):
                raise Exception("Failed to download subtitle")
                
            # Prepare fonts
            if not self.prepare_fonts():
                raise Exception("Failed to prepare fonts")
                
            # Validate inputs
            if not self.validate_inputs():
                raise Exception("Validation failed")
                
            # Convert subtitle
            if not self.convert_subtitle():
                raise Exception("Subtitle conversion failed")
                
            # Process video
            if not self.process_video():
                raise Exception("Video processing failed")
                
            # Upload to Telegram
            success, telegram_link = self.upload_telegram()
            if not success:
                raise Exception("Telegram upload failed")
                
            # Output results for GitHub Actions
            print(f"::set-output name=output_video::{self.output_path}")
            print(f"::set-output name=telegram_link::{telegram_link}")
            print(f"::set-output name=status::completed")
            
            self.log("Processing completed successfully!")
            return True
            
        except Exception as e:
            self.log(f"خطا: {e}")
            print(f"::set-output name=status::failed")
            print(f"::set-output name=error::{str(e)}")
            return False
            
        finally:
            self.cleanup()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: process.py <job_config.json>")
        sys.exit(1)
        
    config_file = Path(sys.argv[1])
    if not config_file.exists():
        print(f"Error: Config file not found: {config_file}")
        sys.exit(1)
        
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
        
    processor = HardsubProcessor(
        job_id=config['job_id'],
        video_url=config['video_url'],
        srt_url=config['srt_url'],
        title=config['title'],
        settings=config['settings']
    )
    
    success = processor.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
