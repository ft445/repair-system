import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'

import pagesConfig from './pages.json'

// 页面组件批量导入
const pageModules = import.meta.glob('./pages/**/*.vue')

const pages = pagesConfig.pages || []
const pageRoutes = pages.map(page => ({
  path: '/' + page.path,
  name: page.path.replace(/\//g, '-'),
  component: pageModules['./' + page.path + '.vue']
}))

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/pages/login/index' },
    ...pageRoutes,
    { path: '/:pathMatch(.*)*', redirect: '/pages/login/index' }
  ]
})

// uni 插件初始化了 window.uni 但只提供了极少数 API
// 这里补充所有页面需要的 uni.* API（不覆盖插件已有的）
if (typeof window !== 'undefined') {
  if (!window.uni) window.uni = {}

  const uni = window.uni

  // ── 存储 ──
  if (!uni.getStorageSync) uni.getStorageSync = (k) => {
    try { return JSON.parse(localStorage.getItem('uni_' + k)) } catch(e) { return localStorage.getItem('uni_' + k) }
  }
  if (!uni.setStorageSync) uni.setStorageSync = (k, v) => {
    localStorage.setItem('uni_' + k, typeof v === 'string' ? v : JSON.stringify(v))
  }
  if (!uni.removeStorageSync) uni.removeStorageSync = (k) => localStorage.removeItem('uni_' + k)
  if (!uni.clearStorageSync) uni.clearStorageSync = () => {
    Object.keys(localStorage).filter(k => k.startsWith('uni_')).forEach(k => localStorage.removeItem(k))
  }

  // ── Toast / Loading ──
  if (!uni.showToast) uni.showToast = (opts) => {
    const el = document.createElement('div')
    el.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:rgba(0,0,0,0.7);color:#fff;padding:12px 24px;border-radius:8px;z-index:9999;font-size:14px;max-width:80%;text-align:center;pointer-events:none'
    el.textContent = opts.title || ''
    document.body.appendChild(el)
    setTimeout(() => el.remove(), opts.duration || 2000)
  }
  if (!uni.showLoading) uni.showLoading = (opts) => {
    const el = document.createElement('div')
    el.id = 'uni-loading'; el.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.3);display:flex;align-items:center;justify-content:center;z-index:9999'
    el.innerHTML = '<div style="background:#fff;padding:24px 32px;border-radius:12px;font-size:15px">' + (opts?.title || '加载中...') + '</div>'
    document.body.appendChild(el)
  }
  if (!uni.hideLoading) uni.hideLoading = () => {
    const el = document.getElementById('uni-loading'); if (el) el.remove()
  }

  // ── 弹窗 ──
  if (!uni.showModal) uni.showModal = (opts) => {
    if (opts.editable) {
      const r = window.prompt(opts.content || opts.title || '', opts.placeholderText || '')
      opts.success?.({ confirm: r !== null, cancel: r === null, content: r || '' })
    } else {
      const c = window.confirm(opts.content || opts.title || '')
      opts.success?.({ confirm: c, cancel: !c })
    }
  }

  // ── 路由导航 ──
  if (!uni.navigateTo) uni.navigateTo = (o) => router.push(o.url)
  if (!uni.redirectTo) uni.redirectTo = (o) => router.replace(o.url)
  if (!uni.reLaunch) uni.reLaunch = (o) => { router.push(o.url) }
  if (!uni.switchTab) uni.switchTab = (o) => { router.push(o.url) }
  if (!uni.navigateBack) uni.navigateBack = () => router.back()
  if (!uni.setNavigationBarTitle) uni.setNavigationBarTitle = (o) => { document.title = o.title || '' }

  // ── TabBar ──
  if (!uni.setTabBarBadge) uni.setTabBarBadge = () => {}
  if (!uni.removeTabBarBadge) uni.removeTabBarBadge = () => {}

  // ── 设备 ──
  if (!uni.vibrateShort) uni.vibrateShort = () => { try { navigator.vibrate(15) } catch(e) {} }
  if (!uni.makePhoneCall) uni.makePhoneCall = (o) => { window.location.href = 'tel:' + o.phoneNumber }
  if (!uni.setClipboardData) uni.setClipboardData = (o) => { try { navigator.clipboard.writeText(o.data) } catch(e) {} }

  // ── 定位 ──
  if (!uni.getLocation) uni.getLocation = (o) => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        p => o.success?.({ latitude: p.coords.latitude, longitude: p.coords.longitude }),
        () => o.fail?.({ errMsg: '定位失败' }),
        { enableHighAccuracy: true }
      )
    } else o.fail?.({ errMsg: '不支持定位' })
  }
  if (!uni.openLocation) uni.openLocation = (o) => {
    window.open('https://uri.amap.com/marker?position=' + o.longitude + ',' + o.latitude, '_blank')
  }

  // ── 相机/相册 ──
  if (!uni.chooseImage) uni.chooseImage = (o) => {
    const inp = document.createElement('input'); inp.type = 'file'; inp.accept = 'image/*'; inp.multiple = (o.count || 1) > 1
    inp.onchange = () => {
      const files = Array.from(inp.files).slice(0, o.count || 1)
      const paths = files.map(f => URL.createObjectURL(f))
      o.success?.({ tempFilePaths: paths, tempFiles: files })
    }
    inp.click()
  }
  if (!uni.chooseVideo) uni.chooseVideo = (o) => {
    const inp = document.createElement('input'); inp.type = 'file'; inp.accept = 'video/*'
    inp.onchange = () => {
      const f = inp.files[0]
      o.success?.({ tempFilePath: URL.createObjectURL(f), tempFile: f })
    }
    inp.click()
  }
  if (!uni.previewImage) uni.previewImage = (o) => {
    const urls = o.urls || (o.current ? [o.current] : o.url ? [o.url] : [])
    if (urls.length) window.open(urls[0], '_blank')
  }

  // ── 网络请求 ──
  if (!uni.request) uni.request = (opts) => {
    const xhr = new XMLHttpRequest()
    xhr.open(opts.method || 'GET', opts.url)
    xhr.responseType = 'text'
    let hasCT = false
    if (opts.header) {
      Object.entries(opts.header).forEach(([k, v]) => {
        xhr.setRequestHeader(k, v)
        if (k.toLowerCase() === 'content-type') hasCT = true
      })
    }
    if (!hasCT) xhr.setRequestHeader('Content-Type', 'application/json')
    xhr.onload = () => {
      let d = xhr.responseText; try { d = JSON.parse(d) } catch(e) {}
      opts.success?.({ data: d, statusCode: xhr.status, header: {} })
    }
    xhr.onerror = () => opts.fail?.({ errMsg: '请求失败' })
    xhr.send(opts.data ? JSON.stringify(opts.data) : null)
  }

  // ── 上传 ──
  if (!uni.uploadFile) uni.uploadFile = (opts) => {
    if (!opts.filePath) return
    const xhr = new XMLHttpRequest()
    xhr.open('POST', opts.url)
    if (opts.header) Object.entries(opts.header).forEach(([k, v]) => xhr.setRequestHeader(k, v))
    xhr.onload = () => {
      let d = xhr.responseText; try { d = JSON.parse(d) } catch(e) {}
      opts.success?.({ data: JSON.stringify(d), statusCode: xhr.status })
    }
    xhr.onerror = () => opts.fail?.({ errMsg: '上传失败' })
    if (opts.filePath.startsWith('blob:')) {
      fetch(opts.filePath).then(r => r.blob()).then(blob => {
        const fd = new FormData(); fd.append('file', blob, 'upload.' + (blob.type?.includes('video')?'mp4':'jpg'))
        xhr.send(fd)
      }).catch(() => opts.fail?.({ errMsg: '上传失败' }))
    } else {
      xhr.send(opts.filePath)
    }
  }

  // ── WebSocket ──
  if (!uni.connectSocket) uni.connectSocket = (opts) => {
    const ws = new WebSocket(opts.url)
    ws.onopen = () => opts.success?.()
    ws.onerror = (e) => opts.fail?.(e)
    return {
      onOpen: (cb) => { ws.onopen = () => cb() },
      onMessage: (cb) => { ws.onmessage = (e) => cb({ data: e.data }) },
      onClose: (cb) => { ws.onclose = () => cb() },
      onError: (cb) => { ws.onerror = () => cb() },
      send: (d) => { try { ws.send(typeof d === 'string' ? d : JSON.stringify(d)) } catch(e) {} },
      close: () => { try { ws.close() } catch(e) {} },
      get readyState() { return ws.readyState },
    }
  }

  // ── 扫码 ──
  if (!uni.scanCode) uni.scanCode = (opts) => opts.fail?.({ errMsg: '不支持扫码' })

  // ── 下拉刷新 ──
  if (!uni.stopPullDownRefresh) uni.stopPullDownRefresh = () => {}

  // ── 录音 ──
  if (!uni.getRecorderManager) uni.getRecorderManager = () => ({
    start: () => {}, stop: () => {}, onStop: () => {}, onError: () => {}
  })

  // ── 事件 ──
  if (!uni.$emit) {
    const _handlers = new Map()
    uni.$emit = (event, ...args) => window.dispatchEvent(new CustomEvent('uni:' + event, { detail: args }))
    uni.$on = (event, handler) => {
      const wrapped = (e) => handler(...(e.detail || []))
      if (!_handlers.has(event)) _handlers.set(event, new Map())
      _handlers.get(event).set(handler, wrapped)
      window.addEventListener('uni:' + event, wrapped)
    }
    uni.$off = (event, handler) => {
      const handlers = _handlers.get(event)
      if (!handlers) return
      if (handler) {
        const wrapped = handlers.get(handler)
        if (wrapped) { window.removeEventListener('uni:' + event, wrapped); handlers.delete(handler) }
      } else {
        handlers.forEach(w => window.removeEventListener('uni:' + event, w))
        handlers.clear()
      }
    }
  }

  console.log('[UNI] shim ready')
}

const app = createApp(App)
app.use(router)

// ── 全局混入：桥接 uni-app 页面生命周期（onShow/onLoad/onPullDownRefresh）──
app.mixin({
  mounted() {
    const opts = this.$options
    if (typeof opts.onLoad === 'function') opts.onLoad.call(this, this.$route?.query || {})
    if (typeof opts.onShow === 'function') opts.onShow.call(this)
    if (typeof opts.onPullDownRefresh === 'function') {
      let startY = 0
      const ts = (e) => { startY = e.touches[0].screenY }
      const te = (e) => { if (e.changedTouches[0].screenY - startY > 80 && window.scrollY <= 0) opts.onPullDownRefresh.call(this) }
      document.addEventListener('touchstart', ts)
      document.addEventListener('touchend', te)
      this._cleanupPull = () => { document.removeEventListener('touchstart', ts); document.removeEventListener('touchend', te) }
    }
  },
  unmounted() {
    const opts = this.$options
    if (typeof opts.onHide === 'function') opts.onHide.call(this)
    if (typeof opts.onUnload === 'function') opts.onUnload.call(this)
    this._cleanupPull?.()
  }
})

app.mount('#app')
