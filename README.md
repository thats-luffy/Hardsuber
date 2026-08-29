# Hardsub Online - Persian Video Hard-Subtitle Platform

A complete, production-ready online video hard-subtitle platform using GitHub Pages + GitHub Actions + FFmpeg + Python + Telegram Bot API.

## 🎯 Project Architecture

```
┌──────────────────────┐
│   GitHub Pages       │  ← Static Frontend (HTML/CSS/JS)
│   (User Interface)   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Backend API        │  ← Secure job submission & status tracking
│   (Python Server)    │     • Never exposes secrets to frontend
│                      │     • Stores job state persistently
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   GitHub Actions     │  ← Temporary runner for video processing
│   (Workflow)         │     • Downloads video & subtitle
│                      │     • Validates limits (1GB, 30min, 4K)
│                      │     • Runs FFmpeg hardsub
│                      │     • Uploads to Telegram
│                      │     • Cleans up temp files
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Telegram Bot       │  ← Final video delivery
│   (Bot API)          │
└──────────────────────┘
```

## 🔐 Security Architecture

### Why a Backend API is Required

**GitHub Pages alone CANNOT securely trigger GitHub Actions** because:

1. **No secrets in frontend**: A GitHub Personal Access Token (PAT) would be required to call the GitHub Actions API, but putting this in JavaScript would expose it to all users.

2. **Job status persistence**: GitHub Actions doesn't provide a built-in way for the frontend to query job status without credentials.

3. **API key protection**: The backend uses an API key to authenticate status updates from GitHub Actions, preventing unauthorized modifications.

### Solution: Lightweight Backend API

The `backend/api_server.py` provides:

- **Secure job submission**: Accepts job requests from frontend, triggers GitHub Actions server-side
- **Status tracking**: Stores job state in JSON files, accessible via public API
- **API key authentication**: GitHub Actions uses a secret key to update job status
- **No secrets exposed**: Telegram tokens and GitHub PAT never reach the browser

## 📁 Project Structure

```
/workspace/
├── static/
│   ├── index.html          # Main HTML page (RTL/Persian UI)
│   ├── style.css           # Dark modern stylesheet
│   ├── config.js           # Configuration & presets
│   └── app.js              # Frontend JavaScript
│
├── backend/
│   └── api_server.py       # Secure backend API server
│
├── processor/
│   ├── process.py          # Main processing pipeline
│   ├── ffmpeg_utils.py     # FFmpeg command builder
│   ├── subtitle.py         # SRT to ASS converter
│   ├── telegram.py         # Telegram upload handler
│   └── validation.py       # Input validation
│
├── fonts/
│   ├── Vazirmatn-Regular.ttf   # Persian font (regular)
│   └── Vazirmatn-Bold.ttf      # Persian font (bold)
│
├── presets/
│   └── presets.json        # Built-in subtitle presets
│
├── .github/workflows/
│   └── video-processing.yml    # GitHub Actions workflow
│
└── README.md               # This documentation
```

## 🚀 Deployment Guide

### Step 1: Fork/Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/hardsub-platform.git
cd hardsub-platform
```

### Step 2: Configure GitHub Pages

1. Go to repository **Settings** → **Pages**
2. Under "Source", select **Deploy from a branch**
3. Choose branch: **main**, folder: **/static**
4. Click **Save**
5. Your site will be available at: `https://YOUR_USERNAME.github.io/YOUR_REPO/`

### Step 3: Create Telegram Bot

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow prompts to create your bot
4. **Save the bot token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 4: Get Chat ID

1. Add your bot to a channel/group (make it admin if needed)
2. Send a message in the channel
3. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
4. Find the `"chat": {"id": -100XXXXXXXXXX}` in the response
5. **Copy the chat ID** (include the negative sign for channels/groups)

### Step 5: Configure GitHub Secrets

Go to repository **Settings** → **Secrets** → **Actions** → **New repository secret**:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `TELEGRAM_BOT_TOKEN` | `123456789:ABCdef...` | Your Telegram bot token |
| `TELEGRAM_CHAT_ID` | `-1001234567890` | Target channel/group ID |

**Optional** (for production with backend):

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `GITHUB_PAT` | `ghp_...` | Personal Access Token with `workflow` scope |

### Step 6: Deploy Backend API (Production)

For production use, you need to host the backend API somewhere. Options:

#### Option A: Simple VPS/Cloud Server

```bash
# On your server
export GITHUB_OWNER="your-username"
export GITHUB_REPO="hardsub-platform"
export GITHUB_PAT="ghp_your_pat_token"
export BACKEND_PORT=8080

# Run the API server
cd /path/to/hardsub-platform/backend
python3 api_server.py
```

#### Option B: Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/ /app/
EXPOSE 8080
CMD ["python3", "api_server.py"]
```

Then deploy to any container platform (Railway, Render, Fly.io, etc.).

#### Option C: Serverless (Advanced)

Adapt the backend for AWS Lambda, Cloudflare Workers, or similar.

### Step 7: Update Frontend API URL

In `static/config.js`, update the `baseUrl`:

```javascript
const API_CONFIG = {
    baseUrl: 'https://your-backend-domain.com',  // Change for production
    pollInterval: 3000,
    maxRetries: 3
};
```

For local testing, keep it as `window.location.origin`.

## 🎨 Features

### Subtitle Designer

- **Font Family**: Vazirmatn (regular/bold), Vazir
- **Font Size**: 10-150px slider
- **Font Weight**: Normal/Bold toggle
- **Italic**: Toggle
- **Font Color**: Full color picker
- **Outline**: Enable/disable, color, width (0-10)
- **Shadow**: Enable/disable, color, depth (0-10)
- **Background**: Enable/disable, color, opacity (0-100%)
- **Padding**: Horizontal (0-50), Vertical (0-30)
- **Position**: Top/Center/Bottom
- **Alignment**: Right/Center/Left
- **Vertical Margin**: 0-200px

### Built-in Presets

1. **کلاسیک (Classic)**: Clean white text with outline
2. **سفید ضخیم (Bold White)**: Larger bold text
3. **سینمایی (Cinematic)**: Semi-transparent background
4. **مینیمال (Minimal)**: No effects, clean look
5. **پیش‌فرض فارسی (Persian Default)**: Optimized for Persian
6. **نتفلیکس (Netflix-style)**: Black background, high opacity

### Live Preview

- **16:9 aspect ratio** video frame simulation
- **Real-time updates** for all settings
- **Multi-line support** with automatic background expansion
- **Custom test text** input

## ⚙️ Processing Pipeline

### GitHub Actions Workflow

1. **Checkout** repository
2. **Check system resources** (disk, memory, CPU)
3. **Install dependencies** (FFmpeg, libass, Python)
4. **Verify fonts** directory
5. **Create temporary working directory**
6. **Download video** with 1GB size limit enforcement
7. **Validate video** with ffprobe:
   - Duration ≤ 30 minutes
   - Resolution ≤ 4K (3840×2160)
8. **Download subtitle** (SRT format)
9. **Validate subtitle** file
10. **Convert SRT to ASS** with custom styling
11. **Run FFmpeg** hardsub with libass filter
12. **Upload to Telegram** with formatted caption
13. **Cleanup** all temporary files

### Video Limits

| Limit | Value | Enforcement |
|-------|-------|-------------|
| **Max File Size** | 1 GB | Checked during download (Content-Length + streaming) |
| **Max Duration** | 30 minutes | Validated with ffprobe before processing |
| **Max Resolution** | 4K (3840×2160) | Validated with ffprobe before processing |
| **Max Subtitle Size** | 10 MB | Checked during download |

If any limit is exceeded:
- Job is rejected immediately
- Clear Persian error message displayed
- No GitHub Actions resources wasted

### FFmpeg Configuration

```bash
ffmpeg -y -i input.mp4 \
  -vf "libass=filename='subtitle.ass':fontsdir='./fonts'" \
  -c:v libx264 -preset medium -crf 23 \
  -c:a aac -b:a 192k \
  -movflags +faststart \
  output.mp4
```

- **Video Codec**: H.264 (libx264)
- **Quality**: CRF 23 (balanced quality/size)
- **Audio**: AAC 192kbps
- **Subtitle Rendering**: libass filter with custom fonts

## 📊 Job Status System

### Status Values

| Status | Persian | Description |
|--------|---------|-------------|
| `QUEUED` | در صف انتظار | Job created, waiting for runner |
| `DOWNLOADING` | در حال دانلود | Downloading video/subtitle |
| `PROCESSING` | در حال پردازش | Running FFmpeg |
| `UPLOADING` | در حال آپلود به تلگرام | Uploading final video |
| `COMPLETED` | تکمیل شد | Successfully finished |
| `FAILED` | خطا | Error occurred |

### Progress Tracking

Progress is calculated from **real FFmpeg output**:

```
time=00:05:23.45 → 5:23 / 30:00 → 18% progress
```

Not fake timers or random percentages.

### Job Persistence

- **Active jobs**: Stored in `localStorage` (survives page refresh)
- **Job history**: Last 50 jobs kept in `localStorage`
- **Server-side status**: JSON files in backend (for cross-device access)

## 🔧 Local Development

### Run Backend API

```bash
cd backend
export BACKEND_PORT=8080
python3 api_server.py
```

Access at: `http://localhost:8080` (local development only - NOT for production)

**For production deployment, always use:**
- `PUBLIC_API_URL=https://mrluffys.shop`
- NEVER use `localhost` or `api.mrluffys.shop` in production

### Test Without GitHub Actions

The backend has a **development mode** that doesn't require GitHub credentials:

```bash
# No GITHUB_OWNER/REPO/PAT set
python3 backend/api_server.py
```

Jobs will be created but won't actually process (useful for UI testing).

### Manual Video Processing Test

```bash
cd processor
export JOB_ID="TEST-001"
export VIDEO_URL="https://example.com/video.mp4"
export SRT_URL="https://example.com/sub.srt"
export TITLE="Test Video"
export SUBTITLE_CONFIG='{"fontFamily":"Vazirmatn","fontSize":42}'
export TELEGRAM_BOT_TOKEN=""
export TELEGRAM_CHAT_ID=""

python3 process.py
```

## 🛡️ Security Considerations

### What's Protected

✅ **Telegram Bot Token** - Only in GitHub Secrets, never in frontend  
✅ **Telegram Chat ID** - Only in GitHub Secrets  
✅ **GitHub PAT** - Only in backend environment variables  
✅ **API Key** - Generated at runtime, used for callback authentication  

### Input Validation

- **URL validation**: Must be HTTP/HTTPS
- **File extension checks**: Video (.mp4, .mkv, etc.), Subtitle (.srt, .ass)
- **Size limits**: Enforced during download (streaming with byte counting)
- **Duration/resolution**: Validated with ffprobe before expensive processing
- **Command injection prevention**: All subprocess calls use argument arrays

### SSRF Protection

The backend should implement additional protections for production:

- Whitelist allowed domains for video/subtitle URLs
- Block private IP ranges (10.x.x.x, 192.168.x.x, etc.)
- Rate limiting per IP/user

## 🐛 Troubleshooting

### "Workflow trigger failed"

**Cause**: Missing or invalid GitHub PAT in backend.

**Solution**: 
1. Create a PAT with `workflow` scope
2. Set `GITHUB_PAT` environment variable in backend
3. Ensure `GITHUB_OWNER` and `GITHUB_REPO` are correct

### "Telegram upload failed"

**Causes**:
- File too large (>50MB for regular bots)
- Invalid bot token
- Bot not added to target channel

**Solutions**:
1. Check file size (Telegram limit: 50MB)
2. Verify `TELEGRAM_BOT_TOKEN` secret
3. Add bot to channel as admin

### "Insufficient disk space"

GitHub-hosted runners typically have ~14GB free space. If exceeded:

1. Check video size (must be <1GB)
2. Output file will be similar size
3. Ensure 5GB+ free space before starting

### Font not rendering correctly

**Causes**:
- Font file missing or corrupted
- Wrong font name in ASS file

**Solutions**:
1. Verify fonts exist in `fonts/` directory
2. Check font names match exactly (case-sensitive)
3. Use Vazirmatn font family (included)

### Persian text reversed/corrupted

The platform uses:
- UTF-8 encoding throughout
- libass for proper RTL rendering
- Vazirmatn font designed for Persian

If issues occur:
1. Ensure SRT file is UTF-8 encoded
2. Check `Encoding: 1` in ASS file (Unicode)
3. Verify font supports Persian characters

## 📝 API Reference

### Backend API Endpoints

#### `POST /api/job/create`

Create a new processing job.

**Request:**
```json
{
  "video_url": "https://example.com/video.mp4",
  "srt_url": "https://example.com/sub.srt",
  "title": "Episode 1",
  "subtitle_config": { ... }
}
```

**Response:**
```json
{
  "success": true,
  "job_id": "JOB-20240101-A1B2",
  "message": "Workflow triggered successfully",
  "status": "QUEUED"
}
```

#### `GET /api/job/:jobId`

Get job status.

**Response:**
```json
{
  "job_id": "JOB-20240101-A1B2",
  "status": "PROCESSING",
  "current_stage": "Hardsubbing",
  "progress": 45,
  "created_at": "2024-01-01T12:00:00Z",
  "started_at": "2024-01-01T12:01:00Z",
  "completed_at": null,
  "error": null
}
```

#### `GET /api/jobs`

List all jobs (for admin dashboard).

#### `POST /api/job/:jobId/update`

Update job status (requires `X-API-Key` header).

Used by GitHub Actions to report progress.

## 📄 License

This project is provided as-is for educational and practical use.

## 🤝 Contributing

Contributions welcome! Please ensure:
- All code is functional (no TODOs or mocks)
- Persian translations are accurate
- Security best practices followed
- No secrets committed to Git

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review GitHub Actions logs for errors
3. Verify all secrets are configured correctly
4. Test with small video files first

---

**Built with ❤️ for the Persian-speaking community**
