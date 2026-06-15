<template>
  <div class="page">
    <!-- 统计头 -->
    <div class="header-bar">
      <span class="header-title">提现记录</span>
      <span class="header-count" v-if="list.length">共 {{ list.length }} 笔</span>
    </div>

    <!-- 加载 -->
    <div v-if="loading" class="loading-wrap">
      <div class="loading-icon">⏳</div>
      <span class="loading-text">加载中...</span>
    </div>

    <!-- 空状态 -->
    <div v-else-if="list.length === 0" class="empty-state">
      <div class="empty-icon">💳</div>
      <span class="empty-title">暂无提现记录</span>
      <span class="empty-desc">申请提现后将显示在这里</span>
    </div>

    <!-- 列表 -->
    <div v-else class="list-wrap">
      <div v-for="item in list" :key="item.id" class="withdraw-card">
        <div class="wc-top">
          <span class="wc-amount">¥{{ item.amount }}</span>
          <span :class="'wc-status ' + item.status">{{ statusMap[item.status] || item.status }}</span>
        </div>
        <div class="wc-info">
          <span class="wc-method">{{ item.bank_card === 'wechat' ? '微信' : item.bank_card === 'alipay' ? '支付宝' : item.bank_card || '银行卡' }}</span>
          <span class="wc-divider">·</span>
          <span class="wc-time">{{ formatTime(item.created_at) }}</span>
        </div>
        <div class="wc-id">编号: {{ item.id }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../api'
export default {
  data() {
    return {
      user: null, list: [], loading: true,
      statusMap: { pending: '审核中', approved: '已通过', rejected: '已拒绝', done: '已完成' }
    }
  },
  onLoad() {
    this.user = uni.getStorageSync('user')
    if (!this.user) return uni.reLaunch({ url: '/pages/login/index' })
    this.loadData()
  },
  onPullDownRefresh() {
    this.loadData().then(() => uni.stopPullDownRefresh())
  },
  methods: {
    async loadData() {
      this.loading = true
      try {
        const res = await api.getMyWithdrawals(this.user.id)
        this.list = Array.isArray(res.data) ? res.data : []
      } catch(e) { console.error(e) }
      finally { this.loading = false }
    },
    formatTime(t) { if (!t) return ''; return t.slice(0, 16).replace('T', ' ') }
  }
}
</script>

<style>
.page{background:var(--bg-page);min-height:100vh;padding:var(--spacing-md);width:100%;overflow-x:hidden;box-sizing:border-box}
.header-bar{display:flex;justify-content:space-between;align-items:center;margin-bottom:var(--spacing-md)}
.header-title{font-size:var(--font-xl);font-weight:700;color:var(--text-primary)}
.header-count{font-size:var(--font-sm);color:var(--text-tertiary)}
.loading-wrap{text-align:center;padding:60px 0}
.loading-icon{font-size:36px;margin-bottom:var(--spacing-sm)}
.loading-text{font-size:var(--font-base);color:var(--text-tertiary)}
.empty-state{background:var(--bg-card);border-radius:var(--radius-lg);padding:60px 20px;text-align:center;border:1px dashed var(--border-strong)}
.empty-icon{font-size:36px;margin-bottom:var(--spacing-md)}
.empty-title{font-size:var(--font-xl);font-weight:600;color:var(--text-primary);margin-bottom:var(--spacing-xs)}
.empty-desc{font-size:var(--font-base);color:var(--text-tertiary)}
.list-wrap{display:flex;flex-direction:column;gap:var(--spacing-sm)}
.withdraw-card{background:var(--bg-card);border-radius:var(--radius-md);padding:var(--spacing-lg);box-shadow:var(--shadow-sm);border:1px solid var(--border)}
.wc-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:var(--spacing-sm)}
.wc-amount{font-size:24px;font-weight:700;color:var(--text-primary)}
.wc-status{font-size:var(--font-sm);padding:3px 12px;border-radius:var(--radius-round);font-weight:500}
.wc-status.pending{background:var(--warning-bg);color:#d48806}
.wc-status.approved{background:var(--info-bg);color:var(--info)}
.wc-status.rejected{background:var(--danger-bg);color:var(--danger)}
.wc-status.done{background:var(--success-bg);color:var(--success)}
.wc-info{display:flex;align-items:center;gap:6px;font-size:var(--font-sm);color:var(--text-tertiary);margin-bottom:4px}
.wc-divider{color:var(--border)}
.wc-id{font-size:var(--font-sm);color:var(--text-tertiary)}
</style>
