/**
 * Hardsub Platform - Main Application JavaScript
 * Handles UI, live preview, job management, and API communication
 */

// Current subtitle configuration
let currentConfig = { ...DEFAULT_SUBTITLE_CONFIG };

// Active jobs tracking
let activeJobs = new Map();
let jobPollers = new Map();

// DOM Elements
const elements = {};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    initializeElements();
    initializePresets();
    initializeEventListeners();
    updatePreview();
    loadSavedJobs();
});

/**
 * Initialize DOM element references
 */
function initializeElements() {
    // Input fields
    elements.videoTitle = document.getElementById('videoTitle');
    elements.videoUrl = document.getElementById('videoUrl');
    elements.srtUrl = document.getElementById('srtUrl');
    
    // Settings inputs
    elements.fontFamily = document.getElementById('fontFamily');
    elements.fontSize = document.getElementById('fontSize');
    elements.fontSizeValue = document.getElementById('fontSizeValue');
    elements.bold = document.getElementById('bold');
    elements.italic = document.getElementById('italic');
    elements.fontColor = document.getElementById('fontColor');
    elements.fontColorHex = document.getElementById('fontColorHex');
    
    elements.outlineEnabled = document.getElementById('outlineEnabled');
    elements.outlineColor = document.getElementById('outlineColor');
    elements.outlineColorHex = document.getElementById('outlineColorHex');
    elements.outlineWidth = document.getElementById('outlineWidth');
    elements.outlineWidthValue = document.getElementById('outlineWidthValue');
    
    elements.shadowEnabled = document.getElementById('shadowEnabled');
    elements.shadowColor = document.getElementById('shadowColor');
    elements.shadowColorHex = document.getElementById('shadowColorHex');
    elements.shadowDepth = document.getElementById('shadowDepth');
    elements.shadowDepthValue = document.getElementById('shadowDepthValue');
    
    elements.backgroundEnabled = document.getElementById('backgroundEnabled');
    elements.backgroundColor = document.getElementById('backgroundColor');
    elements.backgroundColorHex = document.getElementById('backgroundColorHex');
    elements.backgroundOpacity = document.getElementById('backgroundOpacity');
    elements.backgroundOpacityValue = document.getElementById('backgroundOpacityValue');
    elements.horizontalPadding = document.getElementById('horizontalPadding');
    elements.horizontalPaddingValue = document.getElementById('horizontalPaddingValue');
    elements.verticalPadding = document.getElementById('verticalPadding');
    elements.verticalPaddingValue = document.getElementById('verticalPaddingValue');
    
    elements.position = document.getElementById('position');
    elements.alignment = document.getElementById('alignment');
    elements.verticalMargin = document.getElementById('verticalMargin');
    elements.verticalMarginValue = document.getElementById('verticalMarginValue');
    
    // Preview elements
    elements.videoPreview = document.getElementById('videoPreview');
    elements.subtitlePreview = document.getElementById('subtitlePreview');
    elements.previewText = document.getElementById('previewText');
    elements.previewTextInput = document.getElementById('previewTextInput');
    
    // Buttons and lists
    elements.startProcessingBtn = document.getElementById('startProcessingBtn');
    elements.resetSettingsBtn = document.getElementById('resetSettingsBtn');
    elements.presetsGrid = document.getElementById('presetsGrid');
    elements.activeJobsList = document.getElementById('activeJobsList');
    elements.jobHistoryList = document.getElementById('jobHistoryList');
    elements.toastContainer = document.getElementById('toastContainer');
}

/**
 * Initialize presets grid
 */
async function initializePresets() {
    const container = elements.presetsGrid;
    container.innerHTML = '';
    
    for (const preset of BUILTIN_PRESETS) {
        const btn = document.createElement('button');
        btn.className = 'preset-btn';
        btn.textContent = preset.name;
        btn.onclick = () => applyPreset(preset.config);
        container.appendChild(btn);
    }
    
    // Load custom presets from localStorage
    const customPresets = JSON.parse(localStorage.getItem('customPresets') || '[]');
    for (const preset of customPresets) {
        const btn = document.createElement('button');
        btn.className = 'preset-btn custom';
        btn.textContent = preset.name;
        btn.onclick = () => applyPreset(preset.config);
        container.appendChild(btn);
    }
}

/**
 * Apply a preset configuration
 */
function applyPreset(config) {
    currentConfig = { ...config };
    syncUIWithConfig();
    updatePreview();
    showToast(`پیش‌تنظیم "${BUILTIN_PRESETS.find(p => p.config === config)?.name || 'سفارشی'}" اعمال شد`);
}

/**
 * Sync UI controls with current configuration
 */
function syncUIWithConfig() {
    elements.fontFamily.value = currentConfig.fontFamily;
    elements.fontSize.value = currentConfig.fontSize;
    elements.fontSizeValue.textContent = currentConfig.fontSize;
    elements.bold.checked = currentConfig.bold;
    elements.italic.checked = currentConfig.italic;
    elements.fontColor.value = currentConfig.fontColor;
    elements.fontColorHex.textContent = currentConfig.fontColor;
    
    elements.outlineEnabled.checked = currentConfig.outlineEnabled;
    elements.outlineColor.value = currentConfig.outlineColor;
    elements.outlineColorHex.textContent = currentConfig.outlineColor;
    elements.outlineWidth.value = currentConfig.outlineWidth;
    elements.outlineWidthValue.textContent = currentConfig.outlineWidth;
    
    elements.shadowEnabled.checked = currentConfig.shadowEnabled;
    elements.shadowColor.value = currentConfig.shadowColor;
    elements.shadowColorHex.textContent = currentConfig.shadowColor;
    elements.shadowDepth.value = currentConfig.shadowDepth;
    elements.shadowDepthValue.textContent = currentConfig.shadowDepth;
    
    elements.backgroundEnabled.checked = currentConfig.backgroundEnabled;
    elements.backgroundColor.value = currentConfig.backgroundColor;
    elements.backgroundColorHex.textContent = currentConfig.backgroundColor;
    elements.backgroundOpacity.value = currentConfig.backgroundOpacity;
    elements.backgroundOpacityValue.textContent = currentConfig.backgroundOpacity;
    elements.horizontalPadding.value = currentConfig.horizontalPadding;
    elements.horizontalPaddingValue.textContent = currentConfig.horizontalPadding;
    elements.verticalPadding.value = currentConfig.verticalPadding;
    elements.verticalPaddingValue.textContent = currentConfig.verticalPadding;
    
    elements.position.value = currentConfig.position;
    elements.alignment.value = currentConfig.alignment;
    elements.verticalMargin.value = currentConfig.verticalMargin;
    elements.verticalMarginValue.textContent = currentConfig.verticalMargin;
}

/**
 * Initialize event listeners
 */
function initializeEventListeners() {
    // Font settings
    elements.fontFamily.addEventListener('change', (e) => {
        currentConfig.fontFamily = e.target.value;
        updatePreview();
    });
    
    elements.fontSize.addEventListener('input', (e) => {
        currentConfig.fontSize = parseInt(e.target.value);
        elements.fontSizeValue.textContent = e.target.value;
        updatePreview();
    });
    
    elements.bold.addEventListener('change', (e) => {
        currentConfig.bold = e.target.checked;
        updatePreview();
    });
    
    elements.italic.addEventListener('change', (e) => {
        currentConfig.italic = e.target.checked;
        updatePreview();
    });
    
    elements.fontColor.addEventListener('input', (e) => {
        currentConfig.fontColor = e.target.value;
        elements.fontColorHex.textContent = e.target.value;
        updatePreview();
    });
    
    // Outline settings
    elements.outlineEnabled.addEventListener('change', (e) => {
        currentConfig.outlineEnabled = e.target.checked;
        updatePreview();
    });
    
    elements.outlineColor.addEventListener('input', (e) => {
        currentConfig.outlineColor = e.target.value;
        elements.outlineColorHex.textContent = e.target.value;
        updatePreview();
    });
    
    elements.outlineWidth.addEventListener('input', (e) => {
        currentConfig.outlineWidth = parseInt(e.target.value);
        elements.outlineWidthValue.textContent = e.target.value;
        updatePreview();
    });
    
    // Shadow settings
    elements.shadowEnabled.addEventListener('change', (e) => {
        currentConfig.shadowEnabled = e.target.checked;
        updatePreview();
    });
    
    elements.shadowColor.addEventListener('input', (e) => {
        currentConfig.shadowColor = e.target.value;
        elements.shadowColorHex.textContent = e.target.value;
        updatePreview();
    });
    
    elements.shadowDepth.addEventListener('input', (e) => {
        currentConfig.shadowDepth = parseInt(e.target.value);
        elements.shadowDepthValue.textContent = e.target.value;
        updatePreview();
    });
    
    // Background settings
    elements.backgroundEnabled.addEventListener('change', (e) => {
        currentConfig.backgroundEnabled = e.target.checked;
        updatePreview();
    });
    
    elements.backgroundColor.addEventListener('input', (e) => {
        currentConfig.backgroundColor = e.target.value;
        elements.backgroundColorHex.textContent = e.target.value;
        updatePreview();
    });
    
    elements.backgroundOpacity.addEventListener('input', (e) => {
        currentConfig.backgroundOpacity = parseInt(e.target.value);
        elements.backgroundOpacityValue.textContent = e.target.value;
        updatePreview();
    });
    
    elements.horizontalPadding.addEventListener('input', (e) => {
        currentConfig.horizontalPadding = parseInt(e.target.value);
        elements.horizontalPaddingValue.textContent = e.target.value;
        updatePreview();
    });
    
    elements.verticalPadding.addEventListener('input', (e) => {
        currentConfig.verticalPadding = parseInt(e.target.value);
        elements.verticalPaddingValue.textContent = e.target.value;
        updatePreview();
    });
    
    // Position settings
    elements.position.addEventListener('change', (e) => {
        currentConfig.position = e.target.value;
        updatePreview();
    });
    
    elements.alignment.addEventListener('change', (e) => {
        currentConfig.alignment = e.target.value;
        updatePreview();
    });
    
    elements.verticalMargin.addEventListener('input', (e) => {
        currentConfig.verticalMargin = parseInt(e.target.value);
        elements.verticalMarginValue.textContent = e.target.value;
        updatePreview();
    });
    
    // Preview text input
    elements.previewTextInput.addEventListener('input', (e) => {
        elements.previewText.innerHTML = e.target.value.replace(/\n/g, '<br>');
    });
    
    // Reset button
    elements.resetSettingsBtn.addEventListener('click', () => {
        currentConfig = { ...DEFAULT_SUBTITLE_CONFIG };
        syncUIWithConfig();
        updatePreview();
        showToast('تنظیمات بازنشانی شد');
    });
    
    // Start processing button
    elements.startProcessingBtn.addEventListener('click', handleStartProcessing);
}

/**
 * Update the live preview based on current configuration
 */
function updatePreview() {
    const preview = elements.subtitlePreview;
    const textEl = elements.previewText;
    
    // Apply font settings
    preview.style.fontFamily = currentConfig.fontFamily;
    preview.style.fontSize = `${currentConfig.fontSize}px`;
    preview.style.fontWeight = currentConfig.bold ? '700' : '400';
    preview.style.fontStyle = currentConfig.italic ? 'italic' : 'normal';
    preview.style.color = currentConfig.fontColor;
    
    // Apply outline (text-shadow trick for outline effect in CSS)
    if (currentConfig.outlineEnabled && currentConfig.outlineWidth > 0) {
        const width = currentConfig.outlineWidth;
        const color = currentConfig.outlineColor;
        const shadows = [];
        
        // Create outline effect using multiple text-shadows
        for (let x = -width; x <= width; x++) {
            for (let y = -width; y <= width; y++) {
                if (x !== 0 || y !== 0) {
                    shadows.push(`${x}px ${y}px 0 ${color}`);
                }
            }
        }
        textEl.style.textShadow = shadows.join(', ');
    } else {
        textEl.style.textShadow = '';
    }
    
    // Add shadow if enabled
    if (currentConfig.shadowEnabled && currentConfig.shadowDepth > 0) {
        const depth = currentConfig.shadowDepth;
        const shadow = `2px 2px ${depth}px ${currentConfig.shadowColor}`;
        textEl.style.textShadow = textEl.style.textShadow 
            ? `${textEl.style.textShadow}, ${shadow}`
            : shadow;
    }
    
    // Apply background
    if (currentConfig.backgroundEnabled) {
        const alpha = currentConfig.backgroundOpacity / 100;
        preview.style.backgroundColor = hexToRgba(currentConfig.backgroundColor, alpha);
        preview.style.padding = `${currentConfig.verticalPadding}px ${currentConfig.horizontalPadding}px`;
        preview.style.borderRadius = '4px';
        preview.style.display = 'inline-block';
    } else {
        preview.style.backgroundColor = 'transparent';
        preview.style.padding = '0';
        preview.style.borderRadius = '0';
        preview.style.display = 'block';
    }
    
    // Apply position
    const verticalPositions = {
        'top': 'flex-start',
        'center': 'center',
        'bottom': 'flex-end'
    };
    
    const horizontalAlignments = {
        'right': 'flex-end',
        'center': 'center',
        'left': 'flex-start'
    };
    
    elements.videoPreview.style.alignItems = verticalPositions[currentConfig.position];
    elements.videoPreview.style.justifyContent = horizontalAlignments[currentConfig.alignment];
    
    // Apply margin
    const margins = {
        'top': { marginBottom: `${currentConfig.verticalMargin}px` },
        'center': {},
        'bottom': { marginTop: `${currentConfig.verticalMargin}px` }
    };
    Object.assign(preview.style, margins[currentConfig.position]);
}

/**
 * Convert hex color to RGBA
 */
function hexToRgba(hex, alpha) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

/**
 * Handle start processing button click
 */
async function handleStartProcessing() {
    const videoUrl = elements.videoUrl.value.trim();
    const srtUrl = elements.srtUrl.value.trim();
    const title = elements.videoTitle.value.trim() || 'Untitled';
    
    // Validate inputs
    if (!videoUrl) {
        showToast('لطفاً لینک ویدیو را وارد کنید', 'error');
        return;
    }
    
    if (!srtUrl) {
        showToast('لطفاً لینک زیرنویس را وارد کنید', 'error');
        return;
    }
    
    // Validate URLs
    if (!isValidUrl(videoUrl)) {
        showToast('لینک ویدیو معتبر نیست', 'error');
        return;
    }
    
    if (!isValidUrl(srtUrl)) {
        showToast('لینک زیرنویس معتبر نیست', 'error');
        return;
    }
    
    // Disable button during submission
    elements.startProcessingBtn.disabled = true;
    elements.startProcessingBtn.textContent = '⏳ در حال ارسال...';
    
    try {
        // Create job via API
        const response = await fetch(`${API_CONFIG.baseUrl}/api/job/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                video_url: videoUrl,
                srt_url: srtUrl,
                title: title,
                subtitle_config: currentConfig
            })
        });
        
        const result = await response.json();
        
        if (result.success || response.ok) {
            const jobId = result.job_id;
            
            // Add to active jobs
            activeJobs.set(jobId, {
                job_id: jobId,
                video_url: videoUrl,
                srt_url: srtUrl,
                title: title,
                subtitle_config: currentConfig,
                status: 'QUEUED',
                current_stage: 'Queued',
                progress: 0,
                created_at: new Date().toISOString()
            });
            
            // Save to localStorage
            saveJobsToLocalStorage();
            
            // Start polling for status
            startJobPolling(jobId);
            
            // Update UI
            renderActiveJobs();
            
            showToast(`پردازش شروع شد: ${jobId}`, 'success');
            
            // Clear inputs
            elements.videoUrl.value = '';
            elements.srtUrl.value = '';
        } else {
            throw new Error(result.error || 'Unknown error');
        }
    } catch (error) {
        console.error('Failed to create job:', error);
        showToast(`خطا در ایجاد پردازش: ${error.message}`, 'error');
    } finally {
        elements.startProcessingBtn.disabled = false;
        elements.startProcessingBtn.textContent = '🚀 شروع پردازش';
    }
}

/**
 * Validate URL format
 */
function isValidUrl(url) {
    try {
        const parsed = new URL(url);
        return parsed.protocol === 'http:' || parsed.protocol === 'https:';
    } catch {
        return false;
    }
}

/**
 * Start polling for job status
 */
function startJobPolling(jobId) {
    if (jobPollers.has(jobId)) {
        clearInterval(jobPollers.get(jobId));
    }
    
    const poller = setInterval(async () => {
        try {
            const response = await fetch(`${API_CONFIG.baseUrl}/api/job/${jobId}`);
            
            if (response.ok) {
                const jobData = await response.json();
                
                // Update job data
                if (activeJobs.has(jobId)) {
                    activeJobs.set(jobId, { ...activeJobs.get(jobId), ...jobData });
                    saveJobsToLocalStorage();
                    renderActiveJobs();
                }
                
                // Check if job is complete or failed
                if (['COMPLETED', 'FAILED'].includes(jobData.status)) {
                    stopJobPolling(jobId);
                    
                    // Move to history
                    moveToHistory(jobId);
                    
                    if (jobData.status === 'COMPLETED') {
                        showToast(`پردازش ${jobId} تکمیل شد`, 'success');
                    } else {
                        showToast(`پردازش ${jobId} با خطا مواجه شد: ${jobData.error || ''}`, 'error');
                    }
                }
            }
        } catch (error) {
            console.error(`Failed to poll job ${jobId}:`, error);
        }
    }, API_CONFIG.pollInterval);
    
    jobPollers.set(jobId, poller);
}

/**
 * Stop polling for job status
 */
function stopJobPolling(jobId) {
    if (jobPollers.has(jobId)) {
        clearInterval(jobPollers.get(jobId));
        jobPollers.delete(jobId);
    }
}

/**
 * Render active jobs list
 */
function renderActiveJobs() {
    const container = elements.activeJobsList;
    
    if (activeJobs.size === 0) {
        container.innerHTML = '<p class="empty-state">هیچ پردازش فعالی وجود ندارد</p>';
        return;
    }
    
    container.innerHTML = '';
    
    for (const [jobId, job] of activeJobs) {
        if (['COMPLETED', 'FAILED'].includes(job.status)) {
            continue; // Skip completed/failed jobs in active list
        }
        
        const jobCard = document.createElement('div');
        jobCard.className = 'job-card';
        
        const statusClass = job.status.toLowerCase();
        const statusText = STATUS_TRANSLATIONS[job.status] || job.status;
        const stageText = STAGE_TRANSLATIONS[job.current_stage] || job.current_stage;
        
        jobCard.innerHTML = `
            <div class="job-header">
                <span class="job-title">${escapeHtml(job.title)}</span>
                <span class="job-status ${statusClass}">${statusText}</span>
            </div>
            <div class="job-id">شناسه: ${jobId}</div>
            <div class="job-stage">${stageText}</div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${job.progress}%"></div>
            </div>
            <div class="progress-text">${toPersianNumber(job.progress)}%</div>
        `;
        
        container.appendChild(jobCard);
    }
}

/**
 * Move job to history
 */
function moveToHistory(jobId) {
    const history = getJobHistory();
    const job = activeJobs.get(jobId);
    
    if (job) {
        history.unshift({
            ...job,
            completed_at: new Date().toISOString()
        });
        
        // Keep only last 50 jobs in history
        if (history.length > 50) {
            history.splice(50);
        }
        
        localStorage.setItem('jobHistory', JSON.stringify(history));
        activeJobs.delete(jobId);
        saveJobsToLocalStorage();
        renderActiveJobs();
        renderJobHistory();
    }
}

/**
 * Get job history from localStorage
 */
function getJobHistory() {
    return JSON.parse(localStorage.getItem('jobHistory') || '[]');
}

/**
 * Render job history
 */
function renderJobHistory() {
    const container = elements.jobHistoryList;
    const history = getJobHistory();
    
    if (history.length === 0) {
        container.innerHTML = '<p class="empty-state">تاریخچه‌ای موجود نیست</p>';
        return;
    }
    
    container.innerHTML = '';
    
    for (const job of history) {
        const jobCard = document.createElement('div');
        jobCard.className = 'job-card';
        
        const statusClass = job.status.toLowerCase();
        const statusText = STATUS_TRANSLATIONS[job.status] || job.status;
        
        jobCard.innerHTML = `
            <div class="job-header">
                <span class="job-title">${escapeHtml(job.title)}</span>
                <span class="job-status ${statusClass}">${statusText}</span>
            </div>
            <div class="job-id">شناسه: ${job.job_id}</div>
            <div class="job-date">تاریخ: ${new Date(job.created_at).toLocaleDateString('fa-IR')}</div>
            ${job.telegram_message_link ? `<a href="${job.telegram_message_link}" target="_blank" class="telegram-link">مشاهده در تلگرام</a>` : ''}
        `;
        
        container.appendChild(jobCard);
    }
}

/**
 * Load saved jobs from localStorage
 */
function loadSavedJobs() {
    const savedJobs = JSON.parse(localStorage.getItem('activeJobs') || '[]');
    
    for (const job of savedJobs) {
        if (!['COMPLETED', 'FAILED'].includes(job.status)) {
            activeJobs.set(job.job_id, job);
            startJobPolling(job.job_id);
        }
    }
    
    renderActiveJobs();
    renderJobHistory();
}

/**
 * Save jobs to localStorage
 */
function saveJobsToLocalStorage() {
    const jobsArray = Array.from(activeJobs.values());
    localStorage.setItem('activeJobs', JSON.stringify(jobsArray));
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    elements.toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
