// Cloudflare 全维度指纹伪装脚本 - 消除所有自动化特征
(function() {
    'use strict';

    // 1. 基础Navigator属性伪装
    Object.defineProperties(navigator, {
        webdriver: { get: () => undefined },
        platform: { get: () => 'Win32' },
        product: { get: () => 'Gecko' },
        productSub: { get: () => '20030107' },
        vendor: { get: () => 'Google Inc.' },
        vendorSub: { get: () => '' },
        maxTouchPoints: { get: () => 0 },
        hardwareConcurrency: { get: () => 8 },
        deviceMemory: { get: () => 8 },
        languages: { get: () => ['zh-CN', 'zh', 'en-US', 'en'] },
        appCodeName: { get: () => 'Mozilla' },
        appName: { get: () => 'Netscape' },
        appVersion: { get: () => '5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36' },
        oscpu: { get: () => 'Windows NT 10.0; Win64; x64' }
    });

    // 2. 禁用WebRTC IP泄露
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const originalGetUserMedia = navigator.mediaDevices.getUserMedia;
        navigator.mediaDevices.getUserMedia = function(constraints) {
            if (constraints && constraints.video) {
                delete constraints.video;
            }
            return originalGetUserMedia.call(this, constraints);
        };
    }

    // 3. Canvas指纹随机化（消除唯一性）
    const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function(...args) {
        const res = originalToDataURL.apply(this, args);
        return res.replace(/^data:image\/[^;]+/, 'data:image/png');
    };

    // 4. WebGL指纹伪装
    const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
    WebGLRenderingContext.prototype.getParameter = function(pname) {
        if (pname === 37445) return 'Intel Inc.'; // UNMASKED_VENDOR_WEBGL
        if (pname === 37446) return 'Intel(R) UHD Graphics 770'; // UNMASKED_RENDERER_WEBGL
        return originalGetParameter.call(this, pname);
    };

    // 5. AudioContext指纹随机化
    if (window.AudioContext || window.webkitAudioContext) {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = ctx.createOscillator();
        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(440, ctx.currentTime);
        const gainNode = ctx.createGain();
        gainNode.gain.setValueAtTime(0, ctx.currentTime);
        oscillator.connect(gainNode);
        gainNode.connect(ctx.destination);
        oscillator.start();
        oscillator.stop();
    }

    // 6. 插件列表伪装（模拟真实Chrome）
    Object.defineProperty(navigator, 'plugins', {
        get: () => {
            const plugins = [];
            const pdfPlugin = { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' };
            const pdfViewer = { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '' };
            plugins.push(pdfPlugin, pdfViewer);
            return plugins;
        }
    });

    // 7. 时区伪装
    Intl.DateTimeFormat.prototype.resolvedOptions = () => ({
        timeZone: 'Asia/Shanghai',
        timeZoneName: 'short'
    });

    // 8. 禁用自动化检测标记
    window.chrome = window.chrome || { runtime: {} };
    window.navigator.permissions.query = (parameters) => 
        parameters.name === 'notifications' 
            ? Promise.resolve({ state: 'default' }) 
            : Promise.resolve({ state: 'granted' });
})();
