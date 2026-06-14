<template>
  <view class="page">
    <view class="summary-bar">
      <view class="summary-item">
        <text class="summary-num">{{ ratings.length }}</text>
        <text class="summary-lbl">评价数</text>
      </view>
      <view class="summary-item">
        <text class="summary-num">{{ avgRating }}</text>
        <text class="summary-lbl">平均评分</text>
      </view>
      <view class="summary-item">
        <text class="summary-num">{{ starDistribution }}</text>
        <text class="summary-lbl">好评率</text>
      </view>
    </view>

    <view v-if="loading" class="loading-wrap">
      <view class="loading-icon">⏳</view>
      <text class="loading-text">加载中...</text>
    </view>

    <view v-else-if="ratings.length === 0" class="empty-state">
      <view class="empty-icon">⭐</view>
      <text class="empty-title">暂无评价</text>
      <text class="empty-desc">完成工单后会显示客户评价</text>
    </view>

    <view v-else class="list-wrap">
      <view v-for="item in ratings" :key="item.id" class="rating-card">
        <view class="rc-header">
          <text class="rc-customer">{{ item.customer_name || '客户' }}</text>
          <text class="rc-stars">{{ '⭐'.repeat(item.rating || 0) }}</text>
        </view>
        <text class="rc-comment" v-if="item.comment">{{ item.comment }}</text>
        <text class="rc-comment rc-no-comment" v-else>该客户未留下文字评价</text>
        <view class="rc-footer">
          <text class="rc-service">{{ item.service_item_name || '维修' }}</text>
          <text class="rc-date">{{ formatTime(item.completed_at || item.created_at) }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import api from '../../api'
export default {
  data() {
    return { user: null, ratings: [], loading: true }
  },
  computed: {
    avgRating() {
      if (!this.ratings.length) return '暂无'
      const sum = this.ratings.reduce((s, o) => s + (o.rating || 0), 0)
      return (sum / this.ratings.length).toFixed(1)
    },
    starDistribution() {
      if (!this.ratings.length) return '0%'
      const good = this.ratings.filter(o => (o.rating || 0) >= 4).length
      return Math.round(good / this.ratings.length * 100) + '%'
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
        const res = await api.getMyRatings(this.user.id)
        const orders = (Array.isArray(res.data) ? res.data : res.data?.items) || []
        this.ratings = orders.filter(o => o.rating != null && o.rating > 0)
      } catch(e) { console.error(e) }
      finally { this.loading = false }
    },
    formatTime(t) { if (!t) return ''; return t.slice(0, 10) }
  }
}
</script>

<style>
.page{background:var(--bg-page);min-height:100vh;padding:var(--spacing-md)}
.summary-bar{display:flex;background:var(--bg-card);border-radius:var(--radius-md);padding:var(--spacing-lg);margin-bottom:var(--spacing-md);box-shadow:var(--shadow-sm);border:1px solid var(--border)}
.summary-item{flex:1;text-align:center}
.summary-num{font-size:var(--font-2xl);font-weight:700;display:block;color:var(--primary)}
.summary-lbl{font-size:var(--font-sm);color:var(--text-tertiary);margin-top:2px;display:block}
.loading-wrap,.empty-state{text-align:center;padding:60px 0;background:var(--bg-card);border-radius:var(--radius-lg);border:1px dashed var(--border-strong)}
.loading-icon,.empty-icon{font-size:36px;margin-bottom:var(--spacing-md)}
.loading-text{font-size:var(--font-base);color:var(--text-tertiary)}
.empty-title{font-size:var(--font-xl);font-weight:600;color:var(--text-primary);margin-bottom:var(--spacing-xs)}
.empty-desc{font-size:var(--font-base);color:var(--text-tertiary)}
.list-wrap{display:flex;flex-direction:column;gap:var(--spacing-sm)}
.rating-card{background:var(--bg-card);border-radius:var(--radius-md);padding:var(--spacing-lg);box-shadow:var(--shadow-sm);border:1px solid var(--border)}
.rc-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}
.rc-customer{font-size:var(--font-md);font-weight:600;color:var(--text-primary)}
.rc-stars{font-size:var(--font-md);color:#faad14}
.rc-comment{font-size:var(--font-base);color:var(--text-secondary);line-height:1.5;display:block;margin-bottom:var(--spacing-sm);padding:var(--spacing-sm) 0;border-top:1px solid var(--border)}
.rc-no-comment{color:var(--text-tertiary);font-style:italic}
.rc-footer{display:flex;justify-content:space-between;font-size:var(--font-sm);color:var(--text-tertiary)}
</style>
