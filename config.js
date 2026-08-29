/**
 * Hardsub Platform - Configuration and Presets
 */

// API Configuration
const API_CONFIG = {
    // Backend API URL - MUST match PUBLIC_API_URL environment variable on backend
    // For production at mrluffys.shop, this should be https://mrluffys.shop
    baseUrl: 'https://mrluffy.shop',
    
    // Job polling interval in milliseconds
    pollInterval: 3000,
    
    // Maximum retry attempts for failed requests
    maxRetries: 3
};

// Video Limits
const VIDEO_LIMITS = {
    maxSizeBytes: 1073741824,      // 1GB
    maxSizeFormatted: '۱ گیگابایت',
    maxDurationSeconds: 1800,       // 30 minutes
    maxDurationFormatted: '۳۰ دقیقه',
    maxResolution: 3840,            // 4K
    maxResolutionFormatted: '4K (3840×2160)'
};

// Subtitle Limits
const SUBTITLE_LIMITS = {
    maxSizeBytes: 10485760,         // 10MB
    maxSizeFormatted: '۱۰ مگابایت'
};

// Default subtitle configuration
const DEFAULT_SUBTITLE_CONFIG = {
    fontFamily: 'Vazirmatn',
    fontSize: 42,
    bold: false,
    italic: false,
    fontColor: '#FFFFFF',
    outlineEnabled: true,
    outlineColor: '#000000',
    outlineWidth: 2,
    shadowEnabled: true,
    shadowColor: '#000000',
    shadowDepth: 2,
    position: 'bottom',
    verticalMargin: 30,
    alignment: 'center',
    backgroundEnabled: true,
    backgroundColor: '#000000',
    backgroundOpacity: 60,
    horizontalPadding: 20,
    verticalPadding: 10
};

// Built-in presets (also loaded from presets.json)
const BUILTIN_PRESETS = [
    {
        id: 'classic',
        name: 'کلاسیک',
        config: {
            fontFamily: 'Vazirmatn',
            fontSize: 42,
            bold: false,
            italic: false,
            fontColor: '#FFFFFF',
            outlineEnabled: true,
            outlineColor: '#000000',
            outlineWidth: 2,
            shadowEnabled: true,
            shadowColor: '#000000',
            shadowDepth: 2,
            position: 'bottom',
            verticalMargin: 30,
            alignment: 'center',
            backgroundEnabled: false,
            backgroundColor: '#000000',
            backgroundOpacity: 60,
            horizontalPadding: 20,
            verticalPadding: 10
        }
    },
    {
        id: 'bold_white',
        name: 'سفید ضخیم',
        config: {
            fontFamily: 'Vazirmatn',
            fontSize: 48,
            bold: true,
            italic: false,
            fontColor: '#FFFFFF',
            outlineEnabled: true,
            outlineColor: '#000000',
            outlineWidth: 3,
            shadowEnabled: true,
            shadowColor: '#000000',
            shadowDepth: 3,
            position: 'bottom',
            verticalMargin: 35,
            alignment: 'center',
            backgroundEnabled: false,
            backgroundColor: '#000000',
            backgroundOpacity: 60,
            horizontalPadding: 20,
            verticalPadding: 10
        }
    },
    {
        id: 'cinematic',
        name: 'سینمایی',
        config: {
            fontFamily: 'Vazirmatn',
            fontSize: 44,
            bold: false,
            italic: false,
            fontColor: '#F0F0F0',
            outlineEnabled: true,
            outlineColor: '#000000',
            outlineWidth: 2,
            shadowEnabled: true,
            shadowColor: '#000000',
            shadowDepth: 3,
            position: 'bottom',
            verticalMargin: 40,
            alignment: 'center',
            backgroundEnabled: true,
            backgroundColor: '#000000',
            backgroundOpacity: 70,
            horizontalPadding: 25,
            verticalPadding: 12
        }
    },
    {
        id: 'minimal',
        name: 'مینیمال',
        config: {
            fontFamily: 'Vazirmatn',
            fontSize: 38,
            bold: false,
            italic: false,
            fontColor: '#FFFFFF',
            outlineEnabled: false,
            outlineColor: '#000000',
            outlineWidth: 0,
            shadowEnabled: false,
            shadowColor: '#000000',
            shadowDepth: 0,
            position: 'bottom',
            verticalMargin: 25,
            alignment: 'center',
            backgroundEnabled: false,
            backgroundColor: '#000000',
            backgroundOpacity: 0,
            horizontalPadding: 15,
            verticalPadding: 8
        }
    },
    {
        id: 'persian_default',
        name: 'پیش‌فرض فارسی',
        config: {
            fontFamily: 'Vazirmatn',
            fontSize: 46,
            bold: true,
            italic: false,
            fontColor: '#FFFFFF',
            outlineEnabled: true,
            outlineColor: '#000000',
            outlineWidth: 2,
            shadowEnabled: true,
            shadowColor: '#000000',
            shadowDepth: 2,
            position: 'bottom',
            verticalMargin: 35,
            alignment: 'center',
            backgroundEnabled: true,
            backgroundColor: '#000000',
            backgroundOpacity: 65,
            horizontalPadding: 22,
            verticalPadding: 12
        }
    },
    {
        id: 'netflix',
        name: 'نتفلیکس',
        config: {
            fontFamily: 'Vazirmatn',
            fontSize: 42,
            bold: false,
            italic: false,
            fontColor: '#FFFFFF',
            outlineEnabled: false,
            outlineColor: '#000000',
            outlineWidth: 0,
            shadowEnabled: true,
            shadowColor: '#000000',
            shadowDepth: 2,
            position: 'bottom',
            verticalMargin: 32,
            alignment: 'center',
            backgroundEnabled: true,
            backgroundColor: '#000000',
            backgroundOpacity: 80,
            horizontalPadding: 20,
            verticalPadding: 10
        }
    }
];

// Status translations
const STATUS_TRANSLATIONS = {
    'QUEUED': 'در صف انتظار',
    'DOWNLOADING': 'در حال دانلود',
    'PROCESSING': 'در حال پردازش',
    'HARDSUBBING': 'در حال هاردساب',
    'UPLOADING': 'در حال آپلود به تلگرام',
    'COMPLETED': 'تکمیل شد',
    'FAILED': 'خطا'
};

// Stage translations
const STAGE_TRANSLATIONS = {
    'Checking system resources': 'بررسی منابع سیستم',
    'Preparing fonts': 'آماده‌سازی فونت‌ها',
    'Downloading video': 'دانلود ویدیو',
    'Video downloaded': 'ویدیو دانلود شد',
    'Validating video': 'اعتبارسنجی ویدیو',
    'Downloading subtitle': 'دانلود زیرنویس',
    'Validating subtitle': 'اعتبارسنجی زیرنویس',
    'Generating subtitle styles': 'تولید استایل زیرنویس',
    'Hardsubbing video': 'هاردساب ویدیو',
    'Hardsubbing': 'هاردساب',
    'Hardsubbing complete': 'هاردساب تکمیل شد',
    'Uploading to Telegram': 'آپلود به تلگرام',
    'Upload complete': 'آپلود تکمیل شد',
    'Error': 'خطا'
};

// Helper functions
function formatBytes(bytes) {
    if (bytes === 0) return '۰ بایت';
    const k = 1024;
    const sizes = ['بایت', 'کیلوبایت', 'مگابایت', 'گیگابایت'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return (bytes / Math.pow(k, i)).toFixed(1) + ' ' + sizes[i];
}

function formatDuration(seconds) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    
    if (h > 0) {
        return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }
    return `${m}:${s.toString().padStart(2, '0')}`;
}

function toPersianNumber(num) {
    const persianDigits = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
    return num.toString().replace(/\d/g, x => persianDigits[x]);
}

function generateJobId() {
    const timestamp = new Date().toISOString().slice(0, 10).replace(/-/g, '');
    const randomPart = Math.random().toString(36).substring(2, 6).toUpperCase();
    return `JOB-${timestamp}-${randomPart}`;
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        API_CONFIG,
        VIDEO_LIMITS,
        SUBTITLE_LIMITS,
        DEFAULT_SUBTITLE_CONFIG,
        BUILTIN_PRESETS,
        STATUS_TRANSLATIONS,
        STAGE_TRANSLATIONS,
        formatBytes,
        formatDuration,
        toPersianNumber,
        generateJobId
    };
}
