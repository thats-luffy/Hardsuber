// Configuration for the hardsub platform
const CONFIG = {
    // Video limits
    MAX_VIDEO_SIZE_MB: 1024, // 1 GB
    MAX_VIDEO_DURATION_MINUTES: 30,
    MAX_SRT_SIZE_MB: 10,
    MAX_RESOLUTION: {
        width: 3840,
        height: 2160
    },
    
    // GitHub repository configuration
    GITHUB_REPO: window.location.hostname.includes('github.io') 
        ? window.location.pathname.split('/')[1] + '/' + window.location.pathname.split('/')[2]
        : 'username/repo-name', // Replace with your actual repo
    
    // API endpoints (for GitHub Actions workflow dispatch)
    WORKFLOW_DISPATCH_URL: 'https://api.github.com/repos/USERNAME/REPO/actions/workflows/video-processing.yml/dispatches',
    
    // Storage keys
    STORAGE_KEYS: {
        JOBS: 'hardsub_jobs',
        HISTORY: 'hardsub_history',
        PRESETS: 'hardsub_presets'
    },
    
    // Default subtitle settings
    DEFAULT_SETTINGS: {
        fontFamily: 'Vazirmatn',
        fontSize: 42,
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
        verticalMargin: 30,
        alignment: 'center',
        backgroundEnabled: true,
        backgroundColor: '#000000',
        backgroundOpacity: 60,
        horizontalPadding: 20,
        verticalPadding: 10
    },
    
    // Presets
    PRESETS: {
        classic: {
            fontFamily: 'Vazirmatn',
            fontSize: 42,
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
            verticalMargin: 30,
            alignment: 'center',
            backgroundEnabled: false,
            backgroundColor: '#000000',
            backgroundOpacity: 0,
            horizontalPadding: 20,
            verticalPadding: 10
        },
        boldWhite: {
            fontFamily: 'Vazirmatn',
            fontSize: 48,
            bold: true,
            italic: false,
            fontColor: '#FFFFFF',
            outlineEnabled: true,
            outlineColor: '#000000',
            outlineWidth: 3,
            shadowEnabled: false,
            shadowColor: '#000000',
            shadowDepth: 0,
            position: 'bottom',
            verticalMargin: 40,
            alignment: 'center',
            backgroundEnabled: false,
            backgroundColor: '#000000',
            backgroundOpacity: 0,
            horizontalPadding: 20,
            verticalPadding: 10
        },
        cinematic: {
            fontFamily: 'Vazirmatn',
            fontSize: 45,
            bold: false,
            italic: false,
            fontColor: '#F0F0F0',
            outlineEnabled: true,
            outlineColor: '#000000',
            outlineWidth: 1,
            shadowEnabled: true,
            shadowColor: '#000000',
            shadowDepth: 3,
            position: 'bottom',
            verticalMargin: 50,
            alignment: 'center',
            backgroundEnabled: true,
            backgroundColor: '#000000',
            backgroundOpacity: 70,
            horizontalPadding: 25,
            verticalPadding: 12
        },
        minimal: {
            fontFamily: 'Vazirmatn',
            fontSize: 38,
            bold: false,
            italic: false,
            fontColor: '#FFFFFF',
            outlineEnabled: false,
            outlineColor: '#000000',
            outlineWidth: 0,
            shadowEnabled: true,
            shadowColor: '#000000',
            shadowDepth: 1,
            position: 'bottom',
            verticalMargin: 30,
            alignment: 'center',
            backgroundEnabled: false,
            backgroundColor: '#000000',
            backgroundOpacity: 0,
            horizontalPadding: 15,
            verticalPadding: 8
        },
        persian: {
            fontFamily: 'Vazirmatn',
            fontSize: 44,
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
            backgroundColor: '#1a1a1a',
            backgroundOpacity: 65,
            horizontalPadding: 22,
            verticalPadding: 11
        },
        netflix: {
            fontFamily: 'Vazirmatn',
            fontSize: 40,
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
            verticalMargin: 45,
            alignment: 'center',
            backgroundEnabled: true,
            backgroundColor: '#000000',
            backgroundOpacity: 80,
            horizontalPadding: 20,
            verticalPadding: 10
        }
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}
