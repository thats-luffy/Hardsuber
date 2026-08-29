# GitHub Hardsub Video Processing Platform

A complete, production-ready Persian RTL online video hard-subtitle (hardsub) platform using GitHub Pages + GitHub Actions + FFmpeg + Python + Telegram Bot API.

## 🎬 Features

- **Visual Subtitle Designer** - Real-time preview of subtitle styling
- **Persian/RTL Support** - Full support for Persian, Arabic, and mixed languages
- **Background Processing** - Jobs run on GitHub Actions without keeping browser open
- **Telegram Upload** - Automatic upload to Telegram after processing
- **Video Validation** - Checks size, duration, and resolution limits
- **Custom Presets** - Save and load subtitle styling presets

## 📋 Architecture

```
GitHub Pages (Frontend)
       │
       ▼
Create Processing Job
       │
       ▼
GitHub Actions Workflow
       │
       ▼
Temporary Runner
       │
       ├── Download Video
       ├── Download SRT
       ├── Prepare Fonts
       ├── FFmpeg Hardsub
       ├── Upload to Telegram
       └── Cleanup
```

## 🚀 Setup Instructions

### 1. GitHub Pages Setup

1. Go to your repository Settings → Pages
2. Select "Deploy from a branch"
3. Choose `main` branch and `/ (root)` folder
4. Click Save

### 2. Required GitHub Secrets

Go to Settings → Secrets and variables → Actions and add:

| Secret Name | Description |
|-------------|-------------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Target chat/channel ID for uploads |

### 3. Telegram Bot Setup

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the bot token (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. Add the bot to your target channel/group as admin

### 4. Get Chat ID

For channels:
1. Add your bot as admin to the channel
2. Send a message in the channel
3. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
4. Find `chat.id` in the response (for channels it starts with `-100`)

## ⚙️ Configuration

### Video Limits (configurable in workflow file)

- Maximum video size: 1 GB
- Maximum duration: 30 minutes
- Maximum resolution: 4K (3840×2160)
- Maximum SRT size: 10 MB

### Subtitle Settings

The following settings can be customized:

| Setting | Description | Range |
|---------|-------------|-------|
| Font Family | Vazirmatn, Vazir, Tahoma, Arial | - |
| Font Size | Text size in pixels | 10-150 |
| Bold | Enable bold text | On/Off |
| Italic | Enable italic text | On/Off |
| Font Color | Text color | Any hex color |
| Outline | Text outline/border | On/Off |
| Outline Width | Border thickness | 0-10 |
| Shadow | Drop shadow effect | On/Off |
| Shadow Depth | Shadow distance | 0-10 |
| Background | Subtitle background box | On/Off |
| Background Opacity | Transparency level | 0-100% |
| Position | Vertical position | Top/Center/Bottom |
| Alignment | Text alignment | Left/Center/Right |

## 🔧 Local Development

### Prerequisites

- Python 3.10+
- FFmpeg
- Node.js (optional, for local server)

### Install Dependencies

```bash
pip install requests aiohttp
```

### Run Locally

```bash
# Start a local server
python -m http.server 8000

# Or use any static file server
npx serve .
```

Visit `http://localhost:8000` in your browser.

### Test Processor Locally

```bash
cd processor
python process.py /path/to/job_config.json
```

Example job config:

```json
{
  "job_id": "TEST-001",
  "video_url": "https://example.com/video.mp4",
  "srt_url": "https://example.com/subtitle.srt",
  "title": "Test Video",
  "settings": {
    "fontFamily": "Vazirmatn",
    "fontSize": 42,
    "bold": true,
    "fontColor": "#FFFFFF"
  }
}
```

## 📁 Project Structure

```
/
├── index.html              # Main HTML page
├── style.css               # Stylesheet
├── app.js                  # Frontend JavaScript
├── config.js               # Configuration constants
│
├── fonts/
│   ├── Vazirmatn-Regular.ttf
│   └── Vazirmatn-Bold.ttf
│
├── processor/
│   ├── process.py          # Main processor script
│   ├── ffmpeg_utils.py     # FFmpeg utilities
│   ├── subtitle.py         # SRT to ASS conversion
│   ├── telegram.py         # Telegram upload
│   └── validation.py       # Input validation
│
├── presets/
│   └── presets.json        # Built-in presets
│
├── .github/
│   └── workflows/
│       └── video-processing.yml
│
└── README.md
```

## 🔒 Security

- No secrets exposed in frontend code
- All sensitive data stored in GitHub Secrets
- URL validation on both client and server side
- File size and duration limits enforced
- Temporary files cleaned up after processing
- No command injection vulnerabilities (uses subprocess with argument arrays)

## ⚠️ Troubleshooting

### Workflow fails with "Insufficient disk space"

The runner needs at least 5GB free space. Try:
- Using a smaller video file
- Running during off-peak hours

### Telegram upload fails

Check:
1. Bot token is correct
2. Bot is admin in the target channel
3. Chat ID is correct (includes `-` for channels)

### Font not rendering correctly

Ensure:
1. Font files exist in `fonts/` directory
2. Font name matches exactly in settings
3. FFmpeg can access the fonts directory

### Video exceeds limits

The system enforces:
- Max 1GB file size
- Max 30 minutes duration
- Max 4K resolution

Reduce video size or split into smaller parts.

## 📝 Usage Flow

1. User opens website
2. Enters video URL and SRT URL
3. Opens Subtitle Designer
4. Customizes font, colors, position, etc.
5. Sees real-time preview updates
6. Clicks "شروع پردازش" (Start Processing)
7. Job is created and sent to GitHub Actions
8. Browser can be closed - processing continues
9. When complete, video is uploaded to Telegram
10. User receives link in configured channel

## 🌐 Supported Languages

- Persian (فارسی) ✓
- Arabic (العربية) ✓
- English ✓
- Mixed text ✓
- RTL/LTR bidirectional ✓

## 📄 License

This project is provided as-is for educational and personal use.

## 🤝 Contributing

Contributions are welcome! Please ensure:
- All changes maintain RTL/Persian support
- No secrets are committed
- Tests pass before submitting PR

---

**Made with ❤️ for the Persian-speaking community**
