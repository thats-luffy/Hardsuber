# Hardsub Platform - Deployment Guide

## Architecture Overview

```
User Browser → Python API (mrluffys.shop) → GitHub Actions → Telegram
       ↑              ↓                          ↓
       └──────────────┴──────────────────────────┘
                    Status Callbacks
```

**Key Points:**
- Python API server ONLY manages jobs, NEVER processes videos
- GitHub Actions performs ALL video downloading, processing, and uploading
- Callbacks use PUBLIC_API_URL (NOT localhost)

---

## Required Environment Variables (Python API Host)

### Essential Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `PUBLIC_API_URL` | **CRITICAL**: Public HTTPS URL of your API | `https://api.mrluffys.shop` |
| `API_KEY` | Secret key for GitHub Actions callbacks | Random 64-char hex string |
| `GITHUB_OWNER` | Your GitHub username | `yourusername` |
| `GITHUB_REPO` | Repository name | `hardsub-platform` |
| `GITHUB_PAT` | GitHub Personal Access Token (workflow_dispatch scope) | `ghp_xxxx...` |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_PORT` | `8080` | Port for Python API server |
| `JOB_STATUS_DIR` | `/tmp/hardsub_jobs` | Directory for job status files |
| `ALLOWED_ORIGINS` | `*` | Comma-separated list of allowed CORS origins |

---

## Required GitHub Secrets

Configure these in your GitHub repository settings → Secrets → Actions:

| Secret | Description | How to Obtain |
|--------|-------------|---------------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot API token | From @BotFather on Telegram |
| `TELEGRAM_CHAT_ID` | Chat/channel ID to upload videos | Use @userinfobot or forward a message from your channel to @JsonDumpBot |
| `GITHUB_PAT` | Same as above (or use separate token) | GitHub Settings → Developer Settings → Personal Access Tokens |

---

## Step-by-Step Deployment

### 1. Python API Host Setup (mrluffys.shop)

```bash
# SSH into your Python host
ssh user@mrluffys.shop

# Navigate to project directory
cd /path/to/hardsub-platform

# Create .env file
cat > .env << ENVEOF
PUBLIC_API_URL=https://api.mrluffys.shop
API_KEY=$(openssl rand -hex 32)
GITHUB_OWNER=yourusername
GITHUB_REPO=hardsub-platform
GITHUB_PAT=ghp_your_token_here
BACKEND_PORT=8080
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ENVEOF

# Set proper permissions
chmod 600 .env

# Install dependencies (if any)
pip install --user requests

# Start the server (use systemd or supervisor for production)
nohup python3 backend/api_server.py > api.log 2>&1 &

# Verify it's running
curl http://localhost:8080/api/health
```

### 2. Configure Reverse Proxy (Nginx Example)

```nginx
server {
    listen 443 ssl;
    server_name api.mrluffys.shop;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. GitHub Repository Setup

1. Push code to GitHub:
```bash
git add .
git commit -m "Production deployment"
git push origin main
```

2. Configure GitHub Secrets:
   - Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions`
   - Add secrets: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `GITHUB_PAT`

3. Enable GitHub Actions:
   - Go to: `https://github.com/YOUR_USERNAME/YOUR_REPO/actions`
   - Click "I understand my workflows, go ahead and enable them"

### 4. Frontend Configuration

Update `static/config.js` with your API URL:

```javascript
const API_CONFIG = {
    baseUrl: 'https://api.mrluffys.shop',  // Your public API URL
    pollInterval: 3000,
    maxRetries: 3
};
```

Deploy frontend to GitHub Pages, Netlify, Vercel, or any static hosting.

### 5. Test the Deployment

1. **Health Check:**
```bash
curl https://api.mrluffys.shop/api/health
```

2. **Create a Test Job:**
```bash
curl -X POST https://api.mrluffys.shop/api/job/create \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://example.com/test.mp4",
    "srt_url": "https://example.com/test.srt",
    "title": "Test Video",
    "subtitle_config": {}
  }'
```

3. **Check Job Status:**
```bash
curl https://api.mrluffys.shop/api/job/JOB-XXXXXX/status
```

---

## Troubleshooting

### Callback URL Issues

If GitHub Actions can't reach your API:

1. Verify `PUBLIC_API_URL` is set correctly (HTTPS, no trailing slash)
2. Ensure your firewall allows incoming connections on port 443
3. Check nginx/reverse proxy logs for errors
4. Test callback manually:
```bash
curl -X POST https://api.mrluffys.shop/api/job/TEST-123/update \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{"status": "TEST"}'
```

### Video Processing Fails

1. Check GitHub Actions logs for detailed error messages
2. Verify video URL is publicly accessible (not behind auth)
3. Ensure video meets size/duration limits
4. Check font files exist in `fonts/` directory

### Telegram Upload Fails

1. Verify bot token is valid: `curl https://api.telegram.org/bot<TOKEN>/getMe`
2. Ensure bot is added to the target chat/channel
3. For channels: bot must be admin with "Post Messages" permission
4. File size must be under 50MB (standard bots) or 2GB (premium bots)

---

## Security Checklist

- [ ] API_KEY is a strong random value (64+ characters)
- [ ] GITHUB_PAT has minimal required scopes (only `public_repo` or `repo`)
- [ ] TELEGRAM_BOT_TOKEN is stored only in GitHub Secrets
- [ ] No secrets are exposed in frontend JavaScript
- [ ] HTTPS is enforced for all API endpoints
- [ ] CORS is properly configured (not `*` in production)
- [ ] Rate limiting is considered for abuse prevention

---

## Resource Limits (Configurable)

| Resource | Default | Environment Variable |
|----------|---------|---------------------|
| Max Video Size | 1GB | `MAX_VIDEO_SIZE_BYTES` |
| Max Duration | 30 min | `MAX_DURATION_SECONDS` |
| Max Resolution | 4K (3840px) | `MAX_RESOLUTION` |
| Max SRT Size | 10MB | `MAX_SRT_SIZE_BYTES` |
| Min Disk Space | 5GB | `MIN_DISK_SPACE_BYTES` |
| Telegram Limit | 50MB | `MAX_TELEGRAM_SIZE` |

---

## Support

For issues related to:
- **Python API**: Check `backend/api_server.py` logs
- **Video Processing**: Check GitHub Actions workflow logs
- **Telegram**: Verify bot credentials and permissions
- **Frontend**: Check browser console for errors
