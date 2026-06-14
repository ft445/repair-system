<template>
  <view class="page">
    <!-- 统计头 -->
    <view class="header-bar">
      <text class="header-title">提现记录</text>
      <text class="header-count" v-if="list.length">共 {{ list.length }} 笔</text>
    </view>

    <!-- 加载 -->
    <view v-if="loading" class="loading-wrap">
      <view class="loading-icon">⏳</view>
      <text class="loading-text">加载中...</text>
    </view>

    <!-- 空状态 -->
    <view v-else-if="list.length === 0" class="empty-state">
      <view class="empty-icon">💳</view>
      <text class="empty-title">暂无提现记录</text>
      <text class="empty-desc">申请提现后将显示在这里</text>
    </view>

    <!-- 列表 -->
    <view v-else class="list-wrap">
      <view v-for="item in list" :key="item.id" class="withdraw-card">
        <view class="wc-top">
          <text class="wc-amount">¥{{ item.amount }}</text>
          <text :class="'wc-status ' + item.status">{{ statusMap[item.status] || item.status }}</text>
        </view>
        <view class="wc-info">
          <text class="wc-method">{{ item.bank_card === 'wechat' ? '微信' : item.bank_card === 'alipay' ? '支付宝' : item.bank_card || '银行卡' }}</text>
          <text class="wc-divider">·</text>
          <text class="wc-time">{{ formatTime(item.created_at) }}</text>
        </view>
        <view class="wc-id">编号: {{ item.id }}</view>
      </view>
    </view>
  </view>
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
.page{background:var(--bg-page);min-height:100vh;padding:var(--spacing-md)}
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
