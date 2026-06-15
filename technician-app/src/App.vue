<template>
  <router-view />
  <!-- Tab Bar -->
  <div class="tab-bar" v-if="showTabBar">
    <div v-for="tab in tabItems" :key="tab.pagePath"
      :class="'tab-item ' + (currentTab === tab.pagePath ? 'active' : '')"
      @click="switchTab(tab.pagePath)">
      <span class="tab-icon">{{ tab.icon }}</span>
      <span class="tab-label">{{ tab.text }}</span>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

export default {
  name: 'App',
  setup() {
    const route = useRoute()
    const router = useRouter()

    const tabItems = [
      { pagePath: 'pages/workbench/index', text: '工作台', icon: '🛠' },
      { pagePath: 'pages/orders/index', text: '工单', icon: '📋' },
      { pagePath: 'pages/income/index', text: '收入', icon: '💰' },
      { pagePath: 'pages/profile/index', text: '我的', icon: '👤' },
    ]

    const tabPaths = tabItems.map(t => '/' + t.pagePath)
    const showTabBar = computed(() => tabPaths.includes(route.path))
    const currentTab = computed(() => route.path.replace(/^\//, ''))

    function switchTab(path) {
      router.push('/' + path)
    }

    return { tabItems, showTabBar, currentTab, switchTab }
  },
  mounted() {
    console.log('维修通 师傅端 启动')
    // 尝试初始化 WebSocket 重连（如果之前有 token）
    try {
      const token = uni.getStorageSync('token')
      const user = uni.getStorageSync('user')
      if (token && user?.id) {
        import('./services/websocket').then(m => m.default.connect(user.id, token))
      }
    } catch(e) {}
  }
}
</script>

<style>
/* ====== CSS 变量定义 ====== */
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

/* 全局 */
html { width:100%; overflow-x:hidden; }
body { margin:0; padding:0; background-color: var(--bg-page); font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', sans-serif; color: var(--text-primary); font-size: var(--font-base); min-height: 100vh; width:100%; overflow-x:hidden; -webkit-overflow-scrolling:touch; }
#app { width:100%; max-width:100vw; overflow-x:hidden; }

/* Tab Bar */
.tab-bar {
  position: fixed; bottom: 0; left: 0; right: 0; display: flex;
  background: var(--bg-card); border-top: 1px solid var(--border); z-index: 1000;
  padding-bottom: constant(safe-area-inset-bottom); padding-bottom: env(safe-area-inset-bottom);
  box-shadow: 0 -1px 6px rgba(0,0,0,0.05);
}
.tab-item { flex:1; text-align:center; padding:8px 0; font-size:11px; color:#999; transition:color .2s; }
.tab-item.active { color: var(--primary); }
.tab-icon { font-size:20px; display:block; margin-bottom:2px; }
.tab-label { font-size:10px; }

/* uni-app 兼容层 — 保留旧标签名以兼容可能遗漏的转换 */
view, div { display: block; box-sizing: border-box; }
text, span { display: inline; }
image { display: inline-block; overflow: hidden; object-fit: cover; }

/* 开关组件样式 */
input[type="checkbox"].toggle-switch {
  appearance: none; width: 44px; height: 24px; border-radius: 12px;
  background: #ccc; position: relative; cursor: pointer; transition: .2s;
  border: none; outline: none; flex-shrink: 0;
}
input[type="checkbox"].toggle-switch::after {
  content: ''; position: absolute; top: 2px; left: 2px;
  width: 20px; height: 20px; border-radius: 50%; background: #fff;
  transition: .2s; box-shadow: 0 1px 3px rgba(0,0,0,.2);
}
input[type="checkbox"].toggle-switch:checked { background: #E67A2E; }
input[type="checkbox"].toggle-switch:checked::after { left: 22px; }

/* 所有页面容器 — 防止横向溢出 */
.page { width:100%; max-width:100%; overflow-x:hidden; box-sizing:border-box; }

/* 骨架屏 */
.skeleton-card { background: var(--bg-card); border-radius: var(--radius-md); padding: var(--spacing-lg); margin-bottom: var(--spacing-md); }
.skeleton-line { height:14px; background:linear-gradient(90deg,#f0f0f0 25%,#e8e8e8 50%,#f0f0f0 75%); background-size:200% 100%; border-radius:4px; margin-bottom:8px; animation:shimmer 1.5s ease infinite; }
.skeleton-line.w40 { width:40% } .skeleton-line.w60 { width:60% } .skeleton-line.w80 { width:80% } .skeleton-line.h32 { height:32px } .skeleton-line.h48 { height:48px }
.skeleton-block { background:linear-gradient(90deg,#f0f0f0 25%,#e8e8e8 50%,#f0f0f0 75%); background-size:200% 100%; border-radius:var(--radius-sm); animation:shimmer 1.5s ease infinite; }

@keyframes shimmer { 0% { background-position:-200% 0 } 100% { background-position:200% 0 } }
@keyframes fadeIn { from { opacity:0; transform:translateY(6px) } to { opacity:1; transform:translateY(0) } }
</style>
