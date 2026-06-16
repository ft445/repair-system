<template>
  <router-view />
</template>

<script>
import wsService from './services/websocket'
export default {
  onLaunch() {
    console.log('云匠 师傅端 启动')
    this._autoLogin()
  },
  onShow() {
    this._autoLogin()
  },
  methods: {
    _autoLogin() {
      try {
        const token = uni.getStorageSync('token')
        const user = uni.getStorageSync('user')
        if (!token || !user?.id) return
        // 已登录 → 跳过登录页，直接进工作台
        const pages = getCurrentPages()
        const isLoginPage = pages.length && pages[0].route === 'pages/login/index'
        if (isLoginPage) {
          uni.reLaunch({ url: '/pages/workbench/index' })
        }
        // 连接 WebSocket
        if (!wsService.isConnected()) {
          wsService.connect(user.id, token)
          this._setupListeners()
        }
      } catch(e) {}
    },
    _setupListeners() {
      if (this._listenersReady) return
      this._listenersReady = true
      wsService.onNotification(() => {})
      wsService.onOrderUpdate(() => {})
    }
  }
}
</script>

<style>
page, body, #app {
  --primary: #E67A2E;
  --primary-light: #FFF0E0;
  --primary-gradient: linear-gradient(135deg, #E67A2E, #C96A1F);
  --bg-page: #f5f7fa;
  --bg-card: #ffffff;
  --bg-fill: #f8f9fb;
  --text-primary: #1f2f3a;
  --text-secondary: #5a6e7c;
  --text-tertiary: #8e9aaf;
  --border: #f0f0f0;
  --border-strong: #d9d9d9;
  --success: #52c41a;
  --success-bg: #f6ffed;
  --warning: #f5a623;
  --warning-bg: #fff7e5;
  --danger: #ff4d4f;
  --danger-bg: #fff1f0;
  --info: #1976d2;
  --info-bg: #e3f2fd;
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 14px;
  --radius-xl: 18px;
  --radius-round: 50px;
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 12px;
  --spacing-lg: 16px;
  --spacing-xl: 20px;
  --font-sm: 12px;
  --font-base: 14px;
  --font-md: 15px;
  --font-lg: 17px;
  --font-xl: 20px;
  --font-2xl: 24px;
  --font-3xl: 28px;
  --font-4xl: 36px;
  --shadow-sm: 0 2px 8px rgba(0,0,0,0.04);
}
body {
  margin: 0;
  padding: 0;
  background-color: var(--bg-page);
  font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', sans-serif;
  color: var(--text-primary);
  font-size: var(--font-base);
  min-height: 100vh;
}
view { display: block; box-sizing: border-box; }
text { display: inline; }
</style>
