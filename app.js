// Main Application Logic for Hardsub Platform
class HardsubApp {
    constructor() {
        this.settings = { ...CONFIG.DEFAULT_SETTINGS };
        this.jobs = JSON.parse(localStorage.getItem(CONFIG.STORAGE_KEYS.JOBS) || '[]');
        this.history = JSON.parse(localStorage.getItem(CONFIG.STORAGE_KEYS.HISTORY) || '[]');
        this.customPresets = JSON.parse(localStorage.getItem(CONFIG.STORAGE_KEYS.PRESETS) || '{}');
        
        this.init();
    }
    
    init() {
        this.bindElements();
        this.bindEvents();
        this.updatePreview();
        this.renderJobs();
        this.renderHistory();
        this.loadSettings();
    }
    
    bindElements() {
        // Input elements
        this.videoTitleInput = document.getElementById('videoTitle');
        this.videoUrlInput = document.getElementById('videoUrl');
        this.srtUrlInput = document.getElementById('srtUrl');
        
        // Settings elements
        this.fontFamilySelect = document.getElementById('fontFamily');
        this.fontSizeInput = document.getElementById('fontSize');
        this.fontSizeValue = document.getElementById('fontSizeValue');
        this.boldCheckbox = document.getElementById('bold');
        this.italicCheckbox = document.getElementById('italic');
        this.fontColorInput = document.getElementById('fontColor');
        
        // Outline elements
        this.outlineEnabledCheckbox = document.getElementById('outlineEnabled');
        this.outlineColorInput = document.getElementById('outlineColor');
        this.outlineWidthInput = document.getElementById('outlineWidth');
        this.outlineWidthValue = document.getElementById('outlineWidthValue');
        
        // Shadow elements
        this.shadowEnabledCheckbox = document.getElementById('shadowEnabled');
        this.shadowColorInput = document.getElementById('shadowColor');
        this.shadowDepthInput = document.getElementById('shadowDepth');
        this.shadowDepthValue = document.getElementById('shadowDepthValue');
        
        // Background elements
        this.backgroundEnabledCheckbox = document.getElementById('backgroundEnabled');
        this.backgroundColorInput = document.getElementById('backgroundColor');
        this.backgroundOpacityInput = document.getElementById('backgroundOpacity');
        this.backgroundOpacityValue = document.getElementById('backgroundOpacityValue');
        this.horizontalPaddingInput = document.getElementById('horizontalPadding');
        this.horizontalPaddingValue = document.getElementById('horizontalPaddingValue');
        this.verticalPaddingInput = document.getElementById('verticalPadding');
        this.verticalPaddingValue = document.getElementById('verticalPaddingValue');
        
        // Position elements
        this.positionSelect = document.getElementById('position');
        this.verticalMarginInput = document.getElementById('verticalMargin');
        this.verticalMarginValue = document.getElementById('verticalMarginValue');
        this.alignmentSelect = document.getElementById('alignment');
        
        // Preview elements
        this.previewContainer = document.getElementById('previewContainer');
        this.previewVideo = document.getElementById('previewVideo');
        this.previewSubtitle = document.getElementById('previewSubtitle');
        this.previewText = document.getElementById('previewText');
        this.previewTextInput = document.getElementById('previewTextInput');
        
        // Job elements
        this.startProcessingBtn = document.getElementById('startProcessingBtn');
        this.jobStatus = document.getElementById('jobStatus');
        this.activeJobsList = document.getElementById('activeJobsList');
        this.historyList = document.getElementById('historyList');
        
        // Preset buttons
        this.savePresetBtn = document.getElementById('savePresetBtn');
        this.loadPresetBtn = document.getElementById('loadPresetBtn');
        this.resetSettingsBtn = document.getElementById('resetSettingsBtn');
    }
    
    bindEvents() {
        // Settings change events
        this.fontFamilySelect.addEventListener('change', () => this.updateSetting('fontFamily', this.fontFamilySelect.value));
        this.fontSizeInput.addEventListener('input', () => {
            this.fontSizeValue.textContent = this.fontSizeInput.value;
            this.updateSetting('fontSize', parseInt(this.fontSizeInput.value));
        });
        this.boldCheckbox.addEventListener('change', () => this.updateSetting('bold', this.boldCheckbox.checked));
        this.italicCheckbox.addEventListener('change', () => this.updateSetting('italic', this.italicCheckbox.checked));
        this.fontColorInput.addEventListener('input', () => this.updateSetting('fontColor', this.fontColorInput.value));
        
        // Outline events
        this.outlineEnabledCheckbox.addEventListener('change', () => this.updateSetting('outlineEnabled', this.outlineEnabledCheckbox.checked));
        this.outlineColorInput.addEventListener('input', () => this.updateSetting('outlineColor', this.outlineColorInput.value));
        this.outlineWidthInput.addEventListener('input', () => {
            this.outlineWidthValue.textContent = this.outlineWidthInput.value;
            this.updateSetting('outlineWidth', parseInt(this.outlineWidthInput.value));
        });
        
        // Shadow events
        this.shadowEnabledCheckbox.addEventListener('change', () => this.updateSetting('shadowEnabled', this.shadowEnabledCheckbox.checked));
        this.shadowColorInput.addEventListener('input', () => this.updateSetting('shadowColor', this.shadowColorInput.value));
        this.shadowDepthInput.addEventListener('input', () => {
            this.shadowDepthValue.textContent = this.shadowDepthInput.value;
            this.updateSetting('shadowDepth', parseInt(this.shadowDepthInput.value));
        });
        
        // Background events
        this.backgroundEnabledCheckbox.addEventListener('change', () => this.updateSetting('backgroundEnabled', this.backgroundEnabledCheckbox.checked));
        this.backgroundColorInput.addEventListener('input', () => this.updateSetting('backgroundColor', this.backgroundColorInput.value));
        this.backgroundOpacityInput.addEventListener('input', () => {
            this.backgroundOpacityValue.textContent = this.backgroundOpacityInput.value;
            this.updateSetting('backgroundOpacity', parseInt(this.backgroundOpacityInput.value));
        });
        this.horizontalPaddingInput.addEventListener('input', () => {
            this.horizontalPaddingValue.textContent = this.horizontalPaddingInput.value;
            this.updateSetting('horizontalPadding', parseInt(this.horizontalPaddingInput.value));
        });
        this.verticalPaddingInput.addEventListener('input', () => {
            this.verticalPaddingValue.textContent = this.verticalPaddingInput.value;
            this.updateSetting('verticalPadding', parseInt(this.verticalPaddingInput.value));
        });
        
        // Position events
        this.positionSelect.addEventListener('change', () => this.updateSetting('position', this.positionSelect.value));
        this.verticalMarginInput.addEventListener('input', () => {
            this.verticalMarginValue.textContent = this.verticalMarginInput.value;
            this.updateSetting('verticalMargin', parseInt(this.verticalMarginInput.value));
        });
        this.alignmentSelect.addEventListener('change', () => this.updateSetting('alignment', this.alignmentSelect.value));
        
        // Preview text input
        this.previewTextInput.addEventListener('input', () => {
            this.previewText.innerHTML = this.previewTextInput.value.replace(/\n/g, '<br>');
        });
        
        // Start processing button
        this.startProcessingBtn.addEventListener('click', () => this.startProcessing());
        
        // Preset buttons
        document.querySelectorAll('.preset-btn').forEach(btn => {
            btn.addEventListener('click', () => this.applyPreset(btn.dataset.preset));
        });
        
        this.savePresetBtn.addEventListener('click', () => this.saveCustomPreset());
        this.loadPresetBtn.addEventListener('click', () => this.loadCustomPreset());
        this.resetSettingsBtn.addEventListener('click', () => this.resetSettings());
    }
    
    updateSetting(key, value) {
        this.settings[key] = value;
        this.saveSettings();
        this.updatePreview();
    }
    
    saveSettings() {
        localStorage.setItem('hardsub_current_settings', JSON.stringify(this.settings));
    }
    
    loadSettings() {
        const saved = localStorage.getItem('hardsub_current_settings');
        if (saved) {
            this.settings = JSON.parse(saved);
            this.syncUIWithSettings();
        }
    }
    
    syncUIWithSettings() {
        this.fontFamilySelect.value = this.settings.fontFamily;
        this.fontSizeInput.value = this.settings.fontSize;
        this.fontSizeValue.textContent = this.settings.fontSize;
        this.boldCheckbox.checked = this.settings.bold;
        this.italicCheckbox.checked = this.settings.italic;
        this.fontColorInput.value = this.settings.fontColor;
        
        this.outlineEnabledCheckbox.checked = this.settings.outlineEnabled;
        this.outlineColorInput.value = this.settings.outlineColor;
        this.outlineWidthInput.value = this.settings.outlineWidth;
        this.outlineWidthValue.textContent = this.settings.outlineWidth;
        
        this.shadowEnabledCheckbox.checked = this.settings.shadowEnabled;
        this.shadowColorInput.value = this.settings.shadowColor;
        this.shadowDepthInput.value = this.settings.shadowDepth;
        this.shadowDepthValue.textContent = this.settings.shadowDepth;
        
        this.backgroundEnabledCheckbox.checked = this.settings.backgroundEnabled;
        this.backgroundColorInput.value = this.settings.backgroundColor;
        this.backgroundOpacityInput.value = this.settings.backgroundOpacity;
        this.backgroundOpacityValue.textContent = this.settings.backgroundOpacity;
        this.horizontalPaddingInput.value = this.settings.horizontalPadding;
        this.horizontalPaddingValue.textContent = this.settings.horizontalPadding;
        this.verticalPaddingInput.value = this.settings.verticalPadding;
        this.verticalPaddingValue.textContent = this.settings.verticalPadding;
        
        this.positionSelect.value = this.settings.position;
        this.verticalMarginInput.value = this.settings.verticalMargin;
        this.verticalMarginValue.textContent = this.settings.verticalMargin;
        this.alignmentSelect.value = this.settings.alignment;
    }
    
    updatePreview() {
        const s = this.settings;
        
        // Build font style
        let fontStyle = '';
        if (s.bold) fontStyle += 'bold ';
        if (s.italic) fontStyle += 'italic ';
        fontStyle += `${s.fontSize}px ${s.fontFamily}`;
        
        // Apply to preview text
        this.previewText.style.font = fontStyle;
        this.previewText.style.color = s.fontColor;
        
        // Text shadow (outline + shadow)
        let shadows = [];
        if (s.outlineEnabled && s.outlineWidth > 0) {
            // Create outline effect with multiple shadows
            const ow = s.outlineWidth;
            const oc = s.outlineColor;
            for (let x = -ow; x <= ow; x++) {
                for (let y = -ow; y <= ow; y++) {
                    if (x !== 0 || y !== 0) {
                        shadows.push(`${x}px ${y}px 0 ${oc}`);
                    }
                }
            }
        }
        if (s.shadowEnabled && s.shadowDepth > 0) {
            shadows.push(`${s.shadowDepth}px ${s.shadowDepth}px 3px ${s.shadowColor}`);
        }
        this.previewText.style.textShadow = shadows.join(', ');
        
        // Background
        if (s.backgroundEnabled) {
            const bgColor = this.hexToRgba(s.backgroundColor, s.backgroundOpacity / 100);
            this.previewSubtitle.style.background = bgColor;
            this.previewSubtitle.style.padding = `${s.verticalPadding}px ${s.horizontalPadding}px`;
            this.previewSubtitle.style.borderRadius = '8px';
        } else {
            this.previewSubtitle.style.background = 'transparent';
            this.previewSubtitle.style.padding = '10px 20px';
        }
        
        // Position
        this.previewSubtitle.style.bottom = 'auto';
        this.previewSubtitle.style.top = 'auto';
        this.previewSubtitle.style.left = '50%';
        this.previewSubtitle.style.transform = 'translateX(-50%)';
        
        if (s.position === 'bottom') {
            this.previewSubtitle.style.bottom = `${s.verticalMargin}px`;
        } else if (s.position === 'top') {
            this.previewSubtitle.style.top = `${s.verticalMargin}px`;
        } else if (s.position === 'center') {
            this.previewSubtitle.style.top = '50%';
            this.previewSubtitle.style.transform = 'translate(-50%, -50%)';
        }
        
        // Alignment
        this.previewSubtitle.style.textAlign = s.alignment;
        if (s.alignment === 'right') {
            this.previewSubtitle.style.transform = s.position === 'center' ? 'translateY(-50%)' : 'none';
            this.previewSubtitle.style.left = 'auto';
            this.previewSubtitle.style.right = `${s.verticalMargin}px`;
        } else if (s.alignment === 'left') {
            this.previewSubtitle.style.transform = s.position === 'center' ? 'translateY(-50%)' : 'none';
            this.previewSubtitle.style.left = `${s.verticalMargin}px`;
            this.previewSubtitle.style.right = 'auto';
        }
    }
    
    hexToRgba(hex, alpha) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }
    
    applyPreset(presetName) {
        const preset = CONFIG.PRESETS[presetName];
        if (preset) {
            this.settings = { ...preset };
            this.saveSettings();
            this.syncUIWithSettings();
            this.updatePreview();
        }
    }
    
    saveCustomPreset() {
        const name = prompt('نام پریست خود را وارد کنید:');
        if (name) {
            this.customPresets[name] = { ...this.settings };
            localStorage.setItem(CONFIG.STORAGE_KEYS.PRESETS, JSON.stringify(this.customPresets));
            alert(`پریست "${name}" ذخیره شد.`);
        }
    }
    
    loadCustomPreset() {
        const names = Object.keys(this.customPresets);
        if (names.length === 0) {
            alert('هیچ پریست ذخیره‌شده‌ای وجود ندارد.');
            return;
        }
        const name = prompt('نام پریست را وارد کنید:\n' + names.join('\n'));
        if (name && this.customPresets[name]) {
            this.settings = { ...this.customPresets[name] };
            this.saveSettings();
            this.syncUIWithSettings();
            this.updatePreview();
        }
    }
    
    resetSettings() {
        if (confirm('آیا مطمئن هستید؟ تمام تنظیمات به حالت پیش‌فرض بازمی‌گردند.')) {
            this.settings = { ...CONFIG.DEFAULT_SETTINGS };
            this.saveSettings();
            this.syncUIWithSettings();
            this.updatePreview();
        }
    }
    
    validateInputs() {
        const videoUrl = this.videoUrlInput.value.trim();
        const srtUrl = this.srtUrlInput.value.trim();
        const title = this.videoTitleInput.value.trim();
        
        if (!title) {
            this.showJobStatus('لطفاً عنوان ویدیو را وارد کنید.', 'error');
            return false;
        }
        
        if (!videoUrl) {
            this.showJobStatus('لطفاً لینک ویدیو را وارد کنید.', 'error');
            return false;
        }
        
        if (!srtUrl) {
            this.showJobStatus('لطفاً لینک زیرنویس را وارد کنید.', 'error');
            return false;
        }
        
        // Validate URLs
        try {
            new URL(videoUrl);
            new URL(srtUrl);
        } catch (e) {
            this.showJobStatus('لینک ویدیو یا زیرنویس معتبر نیست.', 'error');
            return false;
        }
        
        // Check HTTPS
        if (!videoUrl.startsWith('http://') && !videoUrl.startsWith('https://')) {
            this.showJobStatus('لینک ویدیو باید با http:// یا https:// شروع شود.', 'error');
            return false;
        }
        
        if (!srtUrl.startsWith('http://') && !srtUrl.startsWith('https://')) {
            this.showJobStatus('لینک زیرنویس باید با http:// یا https:// شروع شود.', 'error');
            return false;
        }
        
        return true;
    }
    
    generateJobId() {
        const timestamp = new Date().toISOString().replace(/[-:]/g, '').slice(0, 8);
        const random = Math.random().toString(36).substring(2, 7).toUpperCase();
        return `JOB-${timestamp}-${random}`;
    }
    
    async startProcessing() {
        if (!this.validateInputs()) {
            return;
        }
        
        const jobId = this.generateJobId();
        const job = {
            id: jobId,
            title: this.videoTitleInput.value.trim(),
            videoUrl: this.videoUrlInput.value.trim(),
            srtUrl: this.srtUrlInput.value.trim(),
            settings: { ...this.settings },
            status: 'queued',
            progress: 0,
            stage: 'queued',
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };
        
        // Save job
        this.jobs.push(job);
        localStorage.setItem(CONFIG.STORAGE_KEYS.JOBS, JSON.stringify(this.jobs));
        
        // Show status
        this.showJobStatus('در حال ایجاد پردازش...', 'info');
        
        // Trigger GitHub Actions workflow
        try {
            await this.triggerWorkflow(job);
            this.renderJobs();
            this.showJobStatus(`پردازش با موفقیت ایجاد شد. شناسه: ${jobId}`, 'success');
        } catch (error) {
            job.status = 'failed';
            job.error = error.message;
            this.saveJobs();
            this.renderJobs();
            this.showJobStatus(`خطا در ایجاد پردازش: ${error.message}`, 'error');
        }
    }
    
    async triggerWorkflow(job) {
        // Note: In a real implementation, you would need a backend service or
        // use GitHub API with proper authentication. For GitHub Pages, you can:
        // 1. Use a serverless function (e.g., GitHub Codespaces, Vercel, Netlify Functions)
        // 2. Store jobs in a GitHub Issue or use a third-party service
        // 3. Manually trigger workflows
        
        // For demonstration, we'll simulate the workflow trigger
        // In production, replace this with actual GitHub API call
        
        console.log('Triggering workflow for job:', job.id);
        
        // Simulate workflow dispatch (in production, use actual GitHub API)
        // This is a placeholder - actual implementation requires backend
        
        // Update job status
        job.status = 'processing';
        job.stage = 'downloading';
        this.saveJobs();
        this.renderJobs();
        
        // In a real implementation, you would call:
        // await fetch(CONFIG.WORKFLOW_DISPATCH_URL, {
        //     method: 'POST',
        //     headers: {
        //         'Authorization': `token ${GITHUB_TOKEN}`,
        //         'Content-Type': 'application/json'
        //     },
        //     body: JSON.stringify({
        //         ref: 'main',
        //         inputs: {
        //             job_id: job.id,
        //             video_url: job.videoUrl,
        //             srt_url: job.srtUrl,
        //             title: job.title,
        //             settings: JSON.stringify(job.settings)
        //         }
        //     })
        // });
        
        // For now, we simulate by storing the job and letting user know
        // that they need to manually trigger or set up proper auth
        
        return { success: true };
    }
    
    saveJobs() {
        localStorage.setItem(CONFIG.STORAGE_KEYS.JOBS, JSON.stringify(this.jobs));
    }
    
    renderJobs() {
        const activeJobs = this.jobs.filter(j => j.status !== 'completed' && j.status !== 'failed');
        
        if (activeJobs.length === 0) {
            this.activeJobsList.innerHTML = '<p class="empty-message">هیچ پردازش فعالی وجود ندارد.</p>';
            return;
        }
        
        this.activeJobsList.innerHTML = activeJobs.map(job => `
            <div class="job-item">
                <div class="job-header">
                    <span class="job-title">${this.escapeHtml(job.title)}</span>
                    <span class="job-id">${job.id}</span>
                </div>
                <div class="job-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${job.progress}%"></div>
                    </div>
                    <div class="progress-text">${job.progress}% - ${this.getStageText(job.stage)}</div>
                </div>
                <div class="job-meta">
                    <span class="job-stage stage-${job.stage}">${this.getStageText(job.stage)}</span>
                    <span>ایجاد شده: ${this.formatDate(job.createdAt)}</span>
                </div>
            </div>
        `).join('');
    }
    
    renderHistory() {
        const completedJobs = this.jobs.filter(j => j.status === 'completed' || j.status === 'failed');
        
        if (completedJobs.length === 0) {
            this.historyList.innerHTML = '<p class="empty-message">تاریخچه‌ای وجود ندارد.</p>';
            return;
        }
        
        this.historyList.innerHTML = completedJobs.map(job => `
            <div class="job-item">
                <div class="job-header">
                    <span class="job-title">${this.escapeHtml(job.title)}</span>
                    <span class="job-id">${job.id}</span>
                </div>
                <div class="job-meta">
                    <span class="job-stage stage-${job.status}">${job.status === 'completed' ? 'تکمیل شد' : 'خطا'}</span>
                    <span>${this.formatDate(job.createdAt)}</span>
                    ${job.telegramLink ? `<a href="${job.telegramLink}" target="_blank" class="text-success">مشاهده در تلگرام</a>` : ''}
                </div>
            </div>
        `).join('');
    }
    
    getStageText(stage) {
        const stages = {
            queued: 'در صف',
            downloading: 'در حال دانلود',
            hardsubbing: 'در حال هاردساب',
            encoding: 'در حال انکود',
            uploading: 'در حال آپلود به تلگرام',
            completed: 'تکمیل شد',
            failed: 'خطا'
        };
        return stages[stage] || stage;
    }
    
    formatDate(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleString('fa-IR');
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    showJobStatus(message, type) {
        this.jobStatus.textContent = message;
        this.jobStatus.className = `job-status ${type}`;
        this.jobStatus.classList.remove('hidden');
        
        setTimeout(() => {
            this.jobStatus.classList.add('hidden');
        }, 5000);
    }
    
    // Method to update job from workflow status
    updateJobStatus(jobId, status, stage, progress, telegramLink = null) {
        const job = this.jobs.find(j => j.id === jobId);
        if (job) {
            job.status = status;
            job.stage = stage;
            job.progress = progress;
            job.updatedAt = new Date().toISOString();
            if (telegramLink) job.telegramLink = telegramLink;
            
            if (status === 'completed' || status === 'failed') {
                // Move to history
                this.jobs = this.jobs.filter(j => j.id !== jobId);
            }
            
            this.saveJobs();
            this.renderJobs();
            this.renderHistory();
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.hardsubApp = new HardsubApp();
});
