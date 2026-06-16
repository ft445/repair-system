<template>
  <view class="page">
    <view class="settings-section">
      <view class="settings-group">
        <view class="settings-item" @click="showServicePhone">
          <text class="si-label">客服电话</text>
          <text class="si-value">{{ servicePhone }}</text>
          <text class="mi-arrow">›</text>
        </view>
        <view class="settings-item" @click="togglePush">
          <text class="si-label">消息推送</text>
          <switch :checked="pushEnabled" color="#E67A2E" @change="togglePush" />
        </view>
        <view class="settings-item" @click="clearCache">
          <text class="si-label">清除缓存</text>
          <text class="si-value">{{ cacheSize }}</text>
          <text class="mi-arrow">›</text>
        </view>
      </view>
    </view>

    <view class="settings-section">
      <view class="settings-group">
        <view class="settings-item" @click="navTo('/pages/profile/about')">
          <text class="si-label">关于云匠</text>
          <text class="mi-arrow">›</text>
        </view>
        <view class="settings-item">
          <text class="si-label">版本号</text>
          <text class="si-value">{{ appVersion }}</text>
        </view>
        <view class="settings-item">
          <text class="si-label">分成比例</text>
          <text class="si-value">{{ commissionRate }}%</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import api from '../../api'
export default {
  data() {
    return {
      servicePhone: '4000000000',
      commissionRate: 80,
      appVersion: '1.0.0',
      pushEnabled: true,
      cacheSize: '计算中...',
      user: null
    }
  },
  onLoad() {
    this.user = uni.getStorageSync('user')
    if (!this.user) return uni.reLaunch({ url: '/pages/login/index' })
    this.loadSettings()
    this.loadVersion()
    this.loadCacheSize()
    this.loadPushSetting()
  },
  methods: {
    navTo(url) { uni.navigateTo({ url }) },
    async loadSettings() {
      try {
        const res = await api.getPublicSettings()
        const d = res.data || {}
        this.servicePhone = d.customer_service_phone || '4000000000'
        this.commissionRate = d.commission_rate || 80
      } catch(e) {}
    },
    loadVersion() {
      // 从 manifest 读取版本号
      try {
        if (typeof plus !== 'undefined') {
          this.appVersion = plus.runtime.version || '1.0.0'
        } else {
          // H5 环境使用 manifest.json 或硬编码
          this.appVersion = '1.1.0'
        }
      } catch(e) { this.appVersion = '1.1.0' }
    },
    loadCacheSize() {
      try {
        const keys = ['token', 'user', 'servicePhone', 'pushEnabled']
        let total = 0
        keys.forEach(k => {
          const v = uni.getStorageSync(k)
          if (v) total += (typeof v === 'string' ? v.length : JSON.stringify(v).length)
        })
        this.cacheSize = total > 1024 ? (total/1024).toFixed(1)+'KB' : total+'B'
      } catch(e) { this.cacheSize = '未知' }
    },
    loadPushSetting() {
      const saved = uni.getStorageSync('pushEnabled')
      this.pushEnabled = saved !== false
    },
    togglePush(e) {
      // e.detail.value for switch event, or we just toggle
      const val = e?.detail?.value !== undefined ? e.detail.value : !this.pushEnabled
      this.pushEnabled = val
      uni.setStorageSync('pushEnabled', val)
      // 在原生APP中可以注册/注销推送服务
      uni.showToast({ title: val ? '推送已开启' : '推送已关闭', icon: 'none' })
    },
    showServicePhone() {
      uni.makePhoneCall({ phoneNumber: this.servicePhone, fail: () => {} })
    },
    clearCache() {
      uni.showModal({
        title: '提示',
        content: '确定清除缓存？不会影响登录状态',
        success: (r) => {
          if (r.confirm) {
            try {
              // 保留登录信息，清除其他缓存
              const token = uni.getStorageSync('token')
              const user = uni.getStorageSync('user')
              uni.clearStorageSync()
              uni.setStorageSync('token', token)
              uni.setStorageSync('user', user)
              this.cacheSize = '0B'
              uni.showToast({ title: '缓存已清除', icon: 'success' })
            } catch(e) { uni.showToast({ title: '清除失败', icon: 'none' }) }
          }
        }
      })
    }
  }
}
</script>

<style>
.page{background:var(--bg-page);min-height:100vh;padding:var(--spacing-md)}
.settings-section{margin-bottom:var(--spacing-md)}
.settings-group{background:var(--bg-card);border-radius:var(--radius-md);overflow:hidden;box-shadow:var(--shadow-sm);border:1px solid var(--border)}
.settings-item{display:flex;align-items:center;padding:var(--spacing-lg);border-bottom:1px solid var(--border);font-size:var(--font-md)}
.settings-item:last-child{border-bottom:none}
.settings-item:active{background:var(--bg-fill)}
.si-label{flex:1;color:var(--text-primary);font-weight:500}
.si-value{color:var(--text-tertiary);margin-right:var(--spacing-sm);font-size:var(--font-sm)}
.mi-arrow{color:var(--text-tertiary);font-size:var(--font-xl)}
</style>
