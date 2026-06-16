<script>
export default {
  onLaunch() {
    console.log('云匠 师傅端 启动')
    const token = uni.getStorageSync('token')
    const user = uni.getStorageSync('user')
    if (token && user) {
      uni.switchTab({ url: '/pages/workbench/index' })
    }
  }
}
</script>

<style>
/* ====== CSS 变量定义 ====== */
page {
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

/* 全局样式 */
page {
  background-color: var(--bg-page);
  font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', sans-serif;
  color: var(--text-primary);
  font-size: var(--font-base);
}

/* 骨架屏通用 */
.skeleton-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-md);
}
.skeleton-line {
  height: 14px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e8e8e8 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  border-radius: 4px;
  margin-bottom: 8px;
  animation: shimmer 1.5s ease infinite;
}
.skeleton-line.w40 { width: 40% }
.skeleton-line.w60 { width: 60% }
.skeleton-line.w80 { width: 80% }
.skeleton-line.h32 { height: 32px }
.skeleton-line.h48 { height: 48px }
.skeleton-block {
  background: linear-gradient(90deg, #f0f0f0 25%, #e8e8e8 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  border-radius: var(--radius-sm);
  animation: shimmer 1.5s ease infinite;
}
@keyframes shimmer {
  0% { background-position: -200% 0 }
  100% { background-position: 200% 0 }
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(6px) }
  to { opacity: 1; transform: translateY(0) }
}
</style>
