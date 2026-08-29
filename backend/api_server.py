#!/usr/bin/env python3
"""
Secure Backend API for Hardsub Platform
Handles job submission, status tracking, and GitHub Actions triggering
NEVER exposes secrets to the frontend
"""

import os
import json
import uuid
import time
import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import subprocess
import re

# Configuration
BACKEND_PORT = int(os.environ.get("BACKEND_PORT", "8080"))
GITHUB_OWNER = os.environ.get("GITHUB_OWNER", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "")
GITHUB_PAT = os.environ.get("GITHUB_PAT", "")  # Only used server-side
JOB_STATUS_DIR = Path(os.environ.get("JOB_STATUS_DIR", "/tmp/hardsub_jobs"))
API_KEY = os.environ.get("API_KEY", secrets.token_hex(32))

# Ensure job status directory exists
JOB_STATUS_DIR.mkdir(parents=True, exist_ok=True)

# Valid video URL patterns
VALID_VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv', '.wmv'}
VALID_SRT_EXTENSIONS = {'.srt', '.ass', '.ssa', '.vtt'}


def generate_job_id():
    """Generate a unique job ID"""
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    random_part = secrets.token_hex(4).upper()
    return f"JOB-{timestamp}-{random_part}"


def validate_url(url, allowed_extensions=None):
    """Validate URL format and optionally check extension"""
    if not url:
        return False, "URL is required"
    
    if not url.startswith(('http://', 'https://')):
        return False, "URL must start with http:// or https://"
    
    parsed = urlparse(url)
    if not parsed.netloc:
        return False, "Invalid URL format"
    
    if allowed_extensions:
        path = parsed.path.lower()
        if not any(path.endswith(ext) for ext in allowed_extensions):
            return False, f"Invalid file extension. Allowed: {', '.join(allowed_extensions)}"
    
    return True, ""


def get_job_status_path(job_id):
    """Get the path to a job's status file"""
    safe_id = re.sub(r'[^A-Za-z0-9_-]', '', job_id)
    return JOB_STATUS_DIR / f"{safe_id}.json"


def load_job_status(job_id):
    """Load job status from file"""
    path = get_job_status_path(job_id)
    if not path.exists():
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def save_job_status(job_data):
    """Save job status to file"""
    path = get_job_status_path(job_data['job_id'])
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(job_data, f, indent=2, ensure_ascii=False)


def create_initial_job_status(job_id, video_url, srt_url, title, subtitle_config):
    """Create initial job status entry"""
    now = datetime.utcnow().isoformat() + "Z"
    job_data = {
        "job_id": job_id,
        "video_url": video_url,
        "srt_url": srt_url,
        "title": title,
        "subtitle_config": subtitle_config,
        "status": "QUEUED",
        "current_stage": "Queued",
        "progress": 0,
        "created_at": now,
        "started_at": None,
        "completed_at": None,
        "error": None,
        "github_run_id": None,
        "telegram_message_id": None,
        "telegram_message_link": None
    }
    save_job_status(job_data)
    return job_data


def trigger_github_workflow(job_data):
    """Trigger GitHub Actions workflow securely (server-side only)"""
    if not GITHUB_OWNER or not GITHUB_REPO or not GITHUB_PAT:
        # In development mode without GitHub credentials
        # Just mark as queued for local testing
        job_data["status"] = "QUEUED"
        job_data["current_stage"] = "Development Mode - No GitHub Credentials"
        save_job_status(job_data)
        return True, "Development mode enabled"
    
    workflow_file = "video-processing.yml"
    url = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/actions/workflows/{workflow_file}/dispatches"
    
    headers = {
        "Authorization": f"Bearer {GITHUB_PAT}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    payload = {
        "ref": "main",
        "inputs": {
            "job_id": job_data["job_id"],
            "video_url": job_data["video_url"],
            "srt_url": job_data["srt_url"],
            "title": job_data["title"],
            "subtitle_config": json.dumps(job_data["subtitle_config"]),
            "api_callback_url": f"http://localhost:{BACKEND_PORT}/api/job/{job_data['job_id']}/update",
            "api_key": API_KEY
        }
    }
    
    try:
        import urllib.request
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            if response.status == 204:
                job_data["status"] = "QUEUED"
                save_job_status(job_data)
                return True, "Workflow triggered successfully"
            else:
                return False, f"GitHub API returned status {response.status}"
    except Exception as e:
        return False, f"Failed to trigger workflow: {str(e)}"


def cleanup_old_jobs(max_age_hours=24):
    """Clean up old job status files"""
    cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
    for job_file in JOB_STATUS_DIR.glob("*.json"):
        try:
            with open(job_file, 'r', encoding='utf-8') as f:
                job_data = json.load(f)
            created = datetime.fromisoformat(job_data.get('created_at', '').replace('Z', '+00:00').replace('+00:00', ''))
            if created < cutoff:
                job_file.unlink()
        except Exception:
            pass


class HardsubAPIHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for the Hardsub API"""
    
    def log_message(self, format, *args):
        """Override to suppress default logging"""
        pass
    
    def send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/api/health':
            self.send_json_response({"status": "ok", "timestamp": datetime.utcnow().isoformat()})
        
        elif path.startswith('/api/job/'):
            parts = path.split('/')
            if len(parts) >= 4:
                job_id = parts[3]
                job_data = load_job_status(job_id)
                if job_data:
                    # Remove sensitive data before sending
                    safe_data = {k: v for k, v in job_data.items() 
                                if k not in ['api_callback_url', 'api_key']}
                    self.send_json_response(safe_data)
                else:
                    self.send_json_response({"error": "Job not found"}, 404)
            else:
                self.send_json_response({"error": "Invalid job ID"}, 400)
        
        elif path == '/api/jobs':
            # List all jobs (for admin/dashboard)
            jobs = []
            for job_file in JOB_STATUS_DIR.glob("*.json"):
                try:
                    with open(job_file, 'r', encoding='utf-8') as f:
                        job_data = json.load(f)
                    safe_data = {k: v for k, v in job_data.items() 
                                if k not in ['api_callback_url', 'api_key']}
                    jobs.append(safe_data)
                except Exception:
                    pass
            jobs.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            self.send_json_response({"jobs": jobs})
        
        elif path == '/':
            # Serve static files
            self.serve_static_file('index.html')
        
        elif path.startswith('/static/'):
            filename = path[1:]  # Remove leading /
            self.serve_static_file(filename)
        
        else:
            self.send_json_response({"error": "Not found"}, 404)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed = urlparse(self.path)
        path = parsed.path
        
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
        
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            self.send_json_response({"error": "Invalid JSON"}, 400)
            return
        
        if path == '/api/job/create':
            self.handle_create_job(data)
        
        elif path.endswith('/update'):
            # Job status update from GitHub Actions (requires API key)
            api_key = self.headers.get('X-API-Key', '')
            if api_key != API_KEY:
                self.send_json_response({"error": "Unauthorized"}, 401)
                return
            self.handle_update_job(path, data)
        
        else:
            self.send_json_response({"error": "Not found"}, 404)
    
    def handle_create_job(self, data):
        """Handle job creation request"""
        # Validate required fields
        video_url = data.get('video_url', '')
        srt_url = data.get('srt_url', '')
        title = data.get('title', 'Untitled')
        subtitle_config = data.get('subtitle_config', {})
        
        # Validate URLs
        valid, error = validate_url(video_url)
        if not valid:
            self.send_json_response({"error": f"Invalid video URL: {error}"}, 400)
            return
        
        valid, error = validate_url(srt_url, VALID_SRT_EXTENSIONS)
        if not valid:
            self.send_json_response({"error": f"Invalid SRT URL: {error}"}, 400)
            return
        
        # Validate subtitle config
        if not isinstance(subtitle_config, dict):
            self.send_json_response({"error": "Invalid subtitle configuration"}, 400)
            return
        
        # Generate job ID and create status entry
        job_id = generate_job_id()
        job_data = create_initial_job_status(
            job_id, video_url, srt_url, title, subtitle_config
        )
        
        # Trigger GitHub Actions workflow
        success, message = trigger_github_workflow(job_data)
        
        if success:
            self.send_json_response({
                "success": True,
                "job_id": job_id,
                "message": message,
                "status": job_data["status"]
            })
        else:
            # Still return job ID for tracking, but note the issue
            self.send_json_response({
                "success": True,
                "job_id": job_id,
                "message": f"Job created but workflow trigger failed: {message}",
                "status": job_data["status"],
                "warning": True
            }, 200)
    
    def handle_update_job(self, path, data):
        """Handle job status update from GitHub Actions"""
        # Extract job_id from path
        parts = path.split('/')
        if len(parts) < 5:
            self.send_json_response({"error": "Invalid path"}, 400)
            return
        
        job_id = parts[3]
        job_data = load_job_status(job_id)
        
        if not job_data:
            self.send_json_response({"error": "Job not found"}, 404)
            return
        
        # Update job data
        if 'status' in data:
            job_data['status'] = data['status']
        if 'current_stage' in data:
            job_data['current_stage'] = data['current_stage']
        if 'progress' in data:
            job_data['progress'] = data['progress']
        if 'github_run_id' in data:
            job_data['github_run_id'] = data['github_run_id']
        if 'error' in data:
            job_data['error'] = data['error']
        if 'telegram_message_id' in data:
            job_data['telegram_message_id'] = data['telegram_message_id']
        if 'telegram_message_link' in data:
            job_data['telegram_message_link'] = data['telegram_message_link']
        
        # Set timestamps based on status
        now = datetime.utcnow().isoformat() + "Z"
        if data.get('status') == 'PROCESSING' and not job_data.get('started_at'):
            job_data['started_at'] = now
        if data.get('status') in ['COMPLETED', 'FAILED'] and not job_data.get('completed_at'):
            job_data['completed_at'] = now
        
        save_job_status(job_data)
        self.send_json_response({"success": True})
    
    def serve_static_file(self, filename):
        """Serve static file from the static directory"""
        filepath = Path(__file__).parent / 'static' / filename
        if not filepath.exists():
            # Try root directory
            filepath = Path(__file__).parent / filename
        
        if not filepath.exists():
            self.send_json_response({"error": "File not found"}, 404)
            return
        
        # Determine content type
        content_type = 'text/html'
        if filename.endswith('.css'):
            content_type = 'text/css'
        elif filename.endswith('.js'):
            content_type = 'application/javascript'
        
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        with open(filepath, 'rb') as f:
            self.wfile.write(f.read())


def main():
    """Start the backend API server"""
    server_address = ('', BACKEND_PORT)
    httpd = HTTPServer(server_address, HardsubAPIHandler)
    print(f"Hardsub Backend API running on port {BACKEND_PORT}")
    print(f"API Key: {API_KEY[:8]}... (keep this secret)")
    print(f"Job Status Directory: {JOB_STATUS_DIR}")
    
    # Cleanup old jobs on startup
    cleanup_old_jobs()
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()


if __name__ == '__main__':
    main()
