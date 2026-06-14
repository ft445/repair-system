<template>
  <view class="page">
    <!-- 头部操作栏 -->
    <view class="top-bar">
      <view class="top-tabs">
        <view :class="'tab '+(activeTab==='all'?'active':'')" @click="switchTab('all')">全部</view>
        <view :class="'tab '+(activeTab==='unread'?'active':'')" @click="switchTab('unread')">未读</view>
      </view>
      <text class="mark-btn" @click="markAllRead" v-if="unreadCount > 0">全部已读</text>
    </view>

    <!-- 骨架屏 -->
    <view v-if="loading" class="skeleton-list">
      <view class="skeleton-card" v-for="i in 5" :key="i">
        <view style="display:flex;gap:12px;align-items:center">
          <view class="skeleton-block" style="width:36px;height:36px;border-radius:50%;flex-shrink:0"></view>
          <view style="flex:1"><view class="skeleton-line w60"></view><view class="skeleton-line w80"></view></view>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view v-else-if="list.length === 0" class="empty-state">
      <view class="empty-icon">🔔</view>
      <text class="empty-title">暂无消息</text>
      <text class="empty-desc">当有新工单或审批结果时会通知您</text>
    </view>

    <!-- 通知列表 -->
    <view v-else class="list-wrap">
      <view
        v-for="item in list" :key="item.id"
        :class="'notify-card '+(item.is_read?'read':'unread')"
        @click="openNotify(item)"
      >
        <view class="notify-left">
          <view class="notify-icon" :class="'icon-'+item.type">{{ notifyIcon(item.type) }}</view>
          <view v-if="!item.is_read" class="unread-dot"></view>
        </view>
        <view class="notify-content">
          <view class="notify-header">
            <text class="notify-title">{{ item.title }}</text>
            <text class="notify-time">{{ formatTime(item.created_at) }}</text>
          </view>
          <text class="notify-desc">{{ item.content }}</text>
        </view>
      </view>

      <!-- 加载更多 -->
      <view class="load-more" v-if="hasMore">
        <text class="load-text" @click="loadMore">{{ loadingMore ? '加载中...' : '加载更多' }}</text>
      </view>
      <view class="load-more" v-else-if="list.length > 0">
        <text class="load-text load-end">— 没有更多了 —</text>
      </view>
    </view>
  </view>
</template>

<script>
import api from '../../api'
export default {
  data() {
    return {
      activeTab: 'all',
      list: [],
      page: 1,
      pageSize: 20,
      hasMore: true,
      loading: true,
      loadingMore: false,
      unreadCount: 0,
      user: null,
    }
  },
  onLoad() {
    this.user = uni.getStorageSync('user')
    if (!this.user) return uni.reLaunch({ url: '/pages/login/index' })
  },
  onShow() {
    this.loadData(true)
    this.loadUnreadCount()
  },
  onPullDownRefresh() {
    this.loadData(true).then(() => uni.stopPullDownRefresh())
  },
  methods: {
    notifyIcon(type) {
      const icons = {
        'order_dispatch': '📋', 'order_status': '📋',
        'leave_review': '📅', 'withdraw_review': '💰',
        'deposit_review': '🛡️', 'system': '🔔',
      }
      return icons[type] || '🔔'
    },
    formatTime(t) {
      if (!t) return ''
      const d = new Date(t)
      const now = new Date()
      const diff = now - d
      if (diff < 60000) return '刚刚'
      if (diff < 3600000) return Math.floor(diff/60000) + '分钟前'
      if (diff < 86400000) return Math.floor(diff/3600000) + '小时前'
      if (diff < 172800000) return '昨天 ' + String(d.getHours()).padStart(2,'0') + ':' + String(d.getMinutes()).padStart(2,'0')
      return String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0') + ' ' + String(d.getHours()).padStart(2,'0') + ':' + String(d.getMinutes()).padStart(2,'0')
    },
    switchTab(tab) {
      this.activeTab = tab
      this.loadData(true)
    },
    async loadData(reset) {
      if (reset) { this.page = 1; this.hasMore = true; this.loading = true }
      try {
        const res = await api.getNotifications(this.page, this.pageSize)
        const d = res.data || {}
        const items = d.items || []
        if (reset) {
          this.list = items
        } else {
          this.list = this.list.concat(items)
        }
        this.hasMore = items.length >= this.pageSize
      } catch(e) { console.error(e) }
      finally { this.loading = false; this.loadingMore = false }
    },
    async loadMore() {
      if (this.loadingMore || !this.hasMore) return
      this.loadingMore = true
      this.page++
      this.loadData(false)
    },
    async loadUnreadCount() {
      try {
        const res = await api.getUnreadCount()
        this.unreadCount = res.data?.count || 0
        if (this.unreadCount > 0) {
          try { uni.setTabBarBadge({ index: 3, text: String(this.unreadCount) }) } catch(e) {}
        } else {
          try { uni.removeTabBarBadge({ index: 3 }) } catch(e) {}
        }
      } catch(e) {}
    },
    async markAllRead() {
      try {
        await api.markAllRead()
        this.unreadCount = 0
        try { uni.removeTabBarBadge({ index: 3 }) } catch(e) {}
        this.list.forEach(n => { n.is_read = true })
        uni.showToast({ title: '已全部标记已读', icon: 'none' })
      } catch(e) { uni.showToast({ title: '操作失败', icon: 'none' }) }
    },
    async openNotify(item) {
      // 标记已读
      if (!item.is_read) {
        try {
          await api.markNotificationRead(item.id)
          item.is_read = true
          this.unreadCount = Math.max(0, this.unreadCount - 1)
          if (this.unreadCount <= 0) { try { uni.removeTabBarBadge({ index: 3 }) } catch(e) {} }
        } catch(e) {}
      }
      // 跳转到关联页面
      if (item.ref_type === 'order' && item.ref_id) {
        uni.navigateTo({ url: '/pages/orders/detail?id=' + item.ref_id })
      } else if (item.type === 'leave_review') {
        uni.showToast({ title: item.content, icon: 'none' })
      } else if (item.type === 'withdraw_review') {
        uni.switchTab({ url: '/pages/income/index' })
      } else if (item.ref_id) {
        uni.navigateTo({ url: '/pages/orders/detail?id=' + item.ref_id })
      }
    }
  }
}
</script>

<style>
.page{background:var(--bg-page);min-height:100vh}
.top-bar{background:var(--bg-card);padding:var(--spacing-sm) var(--spacing-lg);display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--border);position:sticky;top:0;z-index:10}
.top-tabs{display:flex;gap:var(--spacing-xs);background:var(--bg-fill);border-radius:var(--radius-sm);padding:3px}
.top-tabs .tab{padding:6px 18px;font-size:var(--font-base);color:var(--text-tertiary);border-radius:var(--radius-sm);font-weight:500}
.top-tabs .tab.active{background:var(--bg-card);color:var(--primary);font-weight:600;box-shadow:0 1px 4px rgba(0,0,0,.06)}
.mark-btn{font-size:var(--font-sm);color:var(--primary);font-weight:500}

.skeleton-list{padding:var(--spacing-lg)}
.skeleton-card{margin-bottom:var(--spacing-md)}

.empty-state{background:var(--bg-card);border-radius:var(--radius-lg);margin:var(--spacing-lg);padding:60px 20px;text-align:center;border:1px dashed var(--border-strong)}
.empty-icon{font-size:36px;margin-bottom:var(--spacing-md)}
.empty-title{font-size:var(--font-xl);font-weight:600;color:var(--text-primary);margin-bottom:var(--spacing-xs)}
.empty-desc{font-size:var(--font-base);color:var(--text-tertiary)}

.list-wrap{padding:var(--spacing-sm) var(--spacing-md)}
.notify-card{background:var(--bg-card);border-radius:var(--radius-md);padding:var(--spacing-md) var(--spacing-lg);margin-bottom:var(--spacing-sm);display:flex;gap:var(--spacing-md);border:1px solid var(--border);transition:all .2s;animation:fadeIn .3s ease}
.notify-card:active{transform:scale(0.98)}
.notify-card.unread{border-left:3px solid var(--primary);background:var(--primary-light)}

.notify-left{position:relative;flex-shrink:0;padding-top:2px}
.notify-icon{width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:18px;background:var(--bg-fill)}
.unread-dot{width:8px;height:8px;border-radius:50%;background:var(--danger);position:absolute;top:0;right:-2px;border:2px solid var(--bg-card)}
.notify-card.unread .unread-dot{border-color:var(--primary-light)}

.notify-content{flex:1;min-width:0}
.notify-header{display:flex;justify-content:space-between;align-items:flex-start;gap:var(--spacing-sm)}
.notify-title{font-size:var(--font-md);font-weight:600;color:var(--text-primary);flex:1;line-height:1.3}
.notify-time{font-size:var(--font-sm);color:var(--text-tertiary);white-space:nowrap;flex-shrink:0}
.notify-desc{font-size:var(--font-base);color:var(--text-secondary);margin-top:4px;line-height:1.4;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}

.load-more{text-align:center;padding:var(--spacing-lg) 0 var(--spacing-xl)}
.load-text{font-size:var(--font-sm);color:var(--primary)}
.load-end{color:var(--text-tertiary)}
</style>
