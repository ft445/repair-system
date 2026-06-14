<template>
  <view class="page">
    <!-- Tabs -->
    <view class="tabs">
      <view v-for="t in tabs" :key="t.key" :class="'tab '+(activeTab===t.key?'active':'')" @click="switchTab(t.key)">{{ t.label }}</view>
    </view>

    <!-- Skeleton -->
    <view v-if="loading" class="order-list">
      <view class="skeleton-card"><view class="skeleton-line w60"></view><view class="skeleton-line w80"></view><view class="skeleton-line w40 h32"></view></view>
      <view class="skeleton-card"><view class="skeleton-line w60"></view><view class="skeleton-line w80"></view><view class="skeleton-line w40 h32"></view></view>
      <view class="skeleton-card"><view class="skeleton-line w60"></view><view class="skeleton-line w80"></view><view class="skeleton-line w40 h32"></view></view>
    </view>

    <!-- Empty -->
    <view v-else-if="orders.length === 0" class="empty-state">
      <view class="empty-circle">{{ emptyIcons[activeTab] || '📋' }}</view>
      <text class="empty-title">{{ emptyTitles[activeTab] || '暂无工单' }}</text>
      <text class="empty-desc">{{ emptyDescs[activeTab] || '有新工单时会在这里显示' }}</text>
    </view>

    <!-- List -->
    <view v-else class="order-list">
      <view v-for="item in orders" :key="item.id" class="order-card" @click="goDetail(item.id)">
        <view class="card-row">
          <view class="card-service">
            <view class="card-service-icon">{{ serviceIcon(item.category_type) }}</view>
            <view>
              <text class="card-service-name">{{ item.service_item_name || '维修' }}</text>
              <text class="card-customer-name">{{ item.customer_name || '客户' }}</text>
            </view>
          </view>
          <text :class="'card-badge ' + item.status">{{ statusLabel(item.status) }}</text>
        </view>
        <view class="card-addr">{{ item.address?.slice(0,30) || '地址待确认' }}</view>
        <view class="card-row card-bottom">
          <view class="card-time">
            <text v-if="item.appointment_time">{{ item.appointment_time.slice(5,10) }} {{ item.appointment_time.slice(11,16) }}</text>
            <text v-else>{{ item.created_at ? parseInt(item.created_at.slice(5,7))+'月'+parseInt(item.created_at.slice(8,10))+'日' : '' }}</text>
          </view>
          <view class="card-right">
            <text class="card-phone" v-if="item.customer_phone">{{ item.customer_phone.slice(0,3)+'****'+item.customer_phone.slice(-4) }}</text>
            <text v-if="item.total_fee" class="card-fee">¥{{ item.total_fee }}</text>
          </view>
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
      tabs: [{key:'',label:'全部'},{key:'pending',label:'待接单'},{key:'in_progress',label:'进行中'},{key:'completed',label:'已完成'}],
      activeTab: '', orders: [], loading: false, user: null,
      emptyIcons: {'':'📋',pending:'📭',in_progress:'🔧',completed:'✅'},
      emptyTitles: {'':'暂无工单',pending:'暂无待接单',in_progress:'暂无进行中',completed:'暂无已完成'},
      emptyDescs: {'':'有新工单时会在这里显示',pending:'请关注新订单通知',in_progress:'接单后开始维修会显示在这里',completed:'完成的工单会显示在这里'}
    }
  },
  onLoad(query) { if (query.status) this.activeTab = query.status; else { var f=uni.getStorageSync('orderFilter'); if(f){this.activeTab=f;uni.removeStorageSync('orderFilter')} } },
  onShow() {
    this.user = uni.getStorageSync('user')
    if (!this.user) return uni.reLaunch({ url: '/pages/login/index' })
    this.loadOrders()
  },
  onPullDownRefresh() { this.loadOrders().then(() => uni.stopPullDownRefresh()) },
  methods: {
    serviceIcon(t) { return t==='维修'?'🔧':t==='安装'?'🔩':t==='清洗'?'🧹':'🔨' },
    statusLabel(s) { const m={pending:'待接单',dispatched:'已派单',accepted:'已接单',in_progress:'进行中',completed:'已完成',paid:'已付款',done:'已完成',cancelled:'已取消'}; return m[s]||s },
    switchTab(k) { this.activeTab = k; this.loadOrders() },
    async loadOrders() {
      this.loading = true
      try {
        const res = await api.getMyOrders(this.user.id)
        let list = (res.data || []).filter(o => o.status !== 'cancelled')
        if (this.activeTab === 'pending') list = list.filter(o => o.status === 'dispatched')
        else if (this.activeTab === 'in_progress') list = list.filter(o => o.status === 'accepted' || o.status === 'in_progress')
        else if (this.activeTab === 'completed') list = list.filter(o => o.status === 'completed' || o.status === 'done' || o.status === 'paid')
        else if (this.activeTab === 'cancel_pending') list = list.filter(o => o.status === 'CANCEL_PENDING')
        this.orders = list
      } catch(e) { console.error(e); uni.showToast({ title:'网络异常，下拉刷新重试', icon:'none' }) }
      finally { this.loading = false }
    },
    goDetail(id) { uni.navigateTo({ url:'/pages/orders/detail?id='+id }) }
  }
}
</script>

<style>
.page{background:var(--bg-page);min-height:100vh;padding:var(--spacing-md)}

/* Tabs */
.tabs{display:flex;background:var(--bg-card);border-radius:var(--radius-md);margin-bottom:var(--spacing-md);padding:4px;box-shadow:var(--shadow-sm)}
.tab{flex:1;text-align:center;padding:8px 0;font-size:var(--font-base);color:var(--text-tertiary);border-radius:var(--radius-sm);font-weight:500;transition:all .2s}
.tab.active{background:var(--primary-gradient);color:#fff;font-weight:600;box-shadow:0 2px 8px rgba(230,122,46,0.25)}

/* Order list */
.order-list{padding-bottom:20px}
.order-card{background:var(--bg-card);border-radius:var(--radius-lg);padding:var(--spacing-lg);margin-bottom:var(--spacing-md);box-shadow:var(--shadow-sm);border:1px solid var(--border);animation:fadeIn .3s ease}
.card-row{display:flex;justify-content:space-between;align-items:center;gap:var(--spacing-sm)}
.card-service{display:flex;align-items:center;gap:var(--spacing-sm);flex:1;min-width:0}
.card-service-icon{font-size:24px;width:36px;height:36px;display:flex;align-items:center;justify-content:center;background:var(--bg-fill);border-radius:var(--radius-sm);flex-shrink:0}
.card-service-name{font-size:var(--font-md);font-weight:600;color:var(--text-primary);display:block;line-height:1.3}
.card-customer-name{font-size:var(--font-sm);color:var(--text-tertiary);display:block}
.card-badge{font-size:var(--font-sm);padding:3px 10px;border-radius:var(--radius-sm);white-space:nowrap;font-weight:500;flex-shrink:0}
.card-badge.pending,.card-badge.dispatched{background:var(--warning-bg);color:#d48806}
.card-badge.in_progress,.card-badge.accepted{background:#fffbe6;color:#d48806}
.card-badge.completed,.card-badge.paid,.card-badge.done{background:var(--success-bg);color:var(--success)}
.card-addr{font-size:var(--font-base);color:var(--text-secondary);margin:var(--spacing-sm) 0;padding:var(--spacing-sm) var(--spacing-md);background:var(--bg-fill);border-radius:var(--radius-sm);line-height:1.4}
.card-bottom{padding-top:var(--spacing-sm);border-top:1px solid var(--border)}
.card-time{font-size:var(--font-sm);color:var(--text-tertiary);display:flex;align-items:center;gap:2px}
.card-right{display:flex;align-items:center;gap:var(--spacing-sm)}
.card-phone{font-size:var(--font-sm);color:var(--text-tertiary)}
.card-fee{color:var(--danger);font-weight:700;font-size:var(--font-md)}

/* Empty state */
.empty-state{background:var(--bg-card);border-radius:var(--radius-lg);margin:0;padding:60px 20px;text-align:center;box-shadow:var(--shadow-sm);border:1px dashed var(--border-strong)}
.empty-circle{width:64px;height:64px;border-radius:50%;background:var(--bg-fill);display:flex;align-items:center;justify-content:center;margin:0 auto var(--spacing-lg);font-size:28px}
.empty-title{font-size:var(--font-xl);font-weight:600;color:var(--text-primary);margin-bottom:var(--spacing-xs)}
.empty-desc{font-size:var(--font-base);color:var(--text-tertiary)}

/* Loading */
.loading-state{display:flex;flex-direction:column;align-items:center;padding:80px 0;color:var(--text-tertiary);gap:var(--spacing-md)}
.loader{width:36px;height:36px;border:3px solid var(--border);border-top-color:var(--primary);border-radius:50%;animation:spin .8s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.loading-text{font-size:var(--font-base)}
</style>
