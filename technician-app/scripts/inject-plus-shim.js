/**
 * 注入 plus 垫片到 index.html，让 uni-app app-plus 构建在标准 WebView 中工作
 * 提供 HBuilder 原生 plus 对象的兼容实现
 */
const fs = require('fs')
const path = require('path')

const htmlPath = path.resolve(__dirname, '../dist/index.html')
let html = fs.readFileSync(htmlPath, 'utf-8')

const shim = `<script>
// Capacitor WebView plus 兼容垫片 - 模拟 HBuilder 原生运行时
window.plus = window.plus || {};
(function() {
  var p = window.plus;
  p.os = { name: 'Android', version: '10' };
  p.runtime = { version: '1.0.0', openURL: function(u) { window.open(u, '_blank'); } };
  p.screen = { getCurrentSize: function() { return { resolutionWidth: 1080, resolutionHeight: 1920 }; } };
  p.navigator = {
    isImmersedStatusbar: false,
    getSafeAreaInsets: function() { return { top: 0, bottom: 0 }; }
  };
  p.key = { showSoftKeybord: function() {} };
  p.webview = {
    currentWebview: function() {
      return { id: 'wv1', app: {}, setStyle: function() {}, getStyle: function() { return {}; },
        show: function() {}, hide: function() {}, evalJS: function() {}, append: function() {} };
    },
    all: function() { return []; },
    create: function() { return p.webview.currentWebview(); },
    postMessageToUniNView: function() {}
  };
  p.io = {
    convertLocalFileSystemURL: function(u) { return u; },
    resolveLocalFileSystemURL: function(u, cb) { if (cb) setTimeout(cb); },
    FileReader: window.FileReader
  };
  p.downloader = { createDownload: function() { return { start: function() {} }; } };
  p.nativeObj = {
    Bitmap: function() { return { clear: function() {}, load: function() {}, draw: function() {} }; }
  };
  p.nativeUI = {
    prompt: function(t, c) { if (c) setTimeout(function() { c({ value: '' }); }); },
    alert: function(t, c) { if (c) setTimeout(c); }
  };
  p.gallery = { pick: function() {} };
  p.barcode = { scan: function() {} };
  p.geolocation = { getCurrentPosition: function(cb, err) { if (err) setTimeout(err); } };
  p.maps = {}; p.video = {}; p.ad = {};
  p.android = {
    requestPermissions: function(perms, cb) {
      if (cb) setTimeout(function() { cb({ deniedAlways: [], deniedPresent: [] }); });
    },
    importClass: function() {}, onResume: function() {}, onPause: function() {},
    onKeyDown: function() {}, onKeyUp: function() {}, onKeyLongPress: function() {},
    onBackKeyPress: function() {}, onMenuKeyPress: function() {}, onSearchKeyPress: function() {}
  };
  window.addEventListener('error', function(e) {
    if (e.message && typeof e.message === 'string' &&
        (e.message.indexOf('__uuid__') !== -1 || e.message.indexOf('plus') !== -1)) {
      e.preventDefault();
    }
  }, true);
  console.log('[CAPACITOR] plus shim ready');
})();
</script>`

html = html.replace('</head>', shim + '</head>')
fs.writeFileSync(htmlPath, html, 'utf-8')
console.log('✓ plus shim injected into dist/index.html')
