<template>
  <div class="page">
    <div class="about-card">
      <div class="about-logo">🛠️</div>
      <div class="about-name">黄师傅维修</div>
      <div class="about-version">v{{ appVersion }}</div>
    </div>

    <div class="info-section">
      <div class="info-row">
        <span class="info-label">应用名称</span>
        <span class="info-value">黄师傅维修 - 师傅端</span>
      </div>
      <div class="info-row">
        <span class="info-label">版本号</span>
        <span class="info-value">{{ appVersion }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">开发团队</span>
        <span class="info-value">黄师傅技术团队</span>
      </div>
      <div class="info-row">
        <span class="info-label">客服热线</span>
        <span class="info-value link" @click="callPhone">{{ servicePhone }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">官方网站</span>
        <span class="info-value link" @click="openSite">www.zpqy.cn</span>
      </div>
    </div>

    <div class="copyright">
      <span>Copyright © 2024-2026 黄师傅维修</span>
      <span>All Rights Reserved</span>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      appVersion: '1.0.0',
      servicePhone: '4000000000'
    }
  },
  onLoad() {
    try {
      if (typeof plus !== 'undefined') {
        this.appVersion = plus.runtime.version || '1.0.0'
      }
    } catch(e) {}
    this.servicePhone = uni.getStorageSync('servicePhone') || '4000000000'
  },
  methods: {
    callPhone() {
      uni.makePhoneCall({ phoneNumber: this.servicePhone, fail: () => {} })
    },
    openSite() {
      plus && plus.runtime.openURL ? plus.runtime.openURL('https://www.zpqy.cn') : uni.showToast({ title: '请在浏览器打开 www.zpqy.cn', icon: 'none' })
    }
  }
}
</script>

<style>
.page{background:var(--bg-page);min-height:100vh;padding:var(--spacing-md);width:100%;overflow-x:hidden;box-sizing:border-box}
.about-card{background:var(--primary-gradient);border-radius:var(--radius-lg);padding:40px 20px;text-align:center;color:#fff;margin-bottom:var(--spacing-md)}
.about-logo{font-size:48px;margin-bottom:var(--spacing-md)}
.about-name{font-size:var(--font-2xl);font-weight:700}
.about-version{font-size:var(--font-base);opacity:.7;margin-top:6px}
.info-section{background:var(--bg-card);border-radius:var(--radius-md);padding:var(--spacing-lg);box-shadow:var(--shadow-sm);border:1px solid var(--border);margin-bottom:var(--spacing-lg)}
.info-row{display:flex;justify-content:space-between;padding:var(--spacing-md) 0;border-bottom:1px solid var(--border)}
.info-row:last-child{border-bottom:none}
.info-label{font-size:var(--font-md);color:var(--text-secondary)}
.info-value{font-size:var(--font-md);color:var(--text-primary);font-weight:500}
.info-value.link{color:var(--primary)}
.copyright{text-align:center;padding:var(--spacing-xl) 0;font-size:var(--font-sm);color:var(--text-tertiary);line-height:1.8}
</style>
