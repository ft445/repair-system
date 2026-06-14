<template>
  <view class="page">
    <view class="header-bar">
      <text class="back-btn" @click="goBack">‹ 返回</text>
      <text class="title-txt">{{ pageTitle }}</text>
      <text style="width:40px"></text>
    </view>

    <view v-if="loading" class="loading-state">
      <view class="skeleton-card"><view class="skeleton-line w60"></view><view class="skeleton-line w80"></view><view class="skeleton-line w40 h32"></view></view>
      <view class="skeleton-card"><view class="skeleton-line w60"></view><view class="skeleton-line w80"></view><view class="skeleton-line w40 h32"></view></view>
    </view>

    <view v-else-if="orders.length === 0" class="empty-state">
      <view class="empty-circle">{{ emptyIcon }}</view>
      <text class="empty-title">{{ emptyTitle }}</text>
      <text class="empty-desc">{{ emptyDesc }}</text>
    </view>

    <view v-else class="list">
      <view v-for="item in orders" :key="item.id" class="task-card" @click="goDetail(item.id)">
        <view class="task-header">
          <text class="task-time">{{ item.created_at ? item.created_at.slice(5,10)+' '+item.created_at.slice(11,16) : '' }}</text>
          <text :class="'task-status ' + item.status">{{ statusTxt(item.status) }}</text>
        </view>
        <view class="task-title">{{ item.service_item_name || '维修' }}
          <text class="task-cate">{{ item.category_type||'' }}</text>
        </view>
        <view class="task-addr">{{ item.address?.slice(0,30) || '' }}</view>
        <view class="task-footer">
          <text class="task-customer">{{ item.customer_name || '客户' }}</text>
          <text class="task-fee" v-if="item.total_fee">¥{{ item.total_fee }}</text>
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
      type: '', orders: [], loading: true,
      titles: { today:'今日上门', tomorrow:'明日上门', pending:'待审核', month:'本月工单', grab:'抢单大厅', accepted:'已接单', in_progress:'进行中', dispatched:'待接单' },
      emptyIcons: { today:'📅', tomorrow:'📆', pending:'✅', month:'📊', grab:'⚡', accepted:'📋', in_progress:'🔧', dispatched:'📭' },
      emptyTitles: { today:'今日暂无上门', tomorrow:'明日暂无上门', pending:'暂无待审核', month:'本月暂无工单', grab:'暂无可以抢的单', accepted:'暂无已接单', in_progress:'暂无进行中', dispatched:'暂无待接单' },
      emptyDescs: { today:'有预约的工单会显示在这里', tomorrow:'明天的预约会显示在这里', pending:'取消待审核的工单会显示在这里', month:'完成的工单会统计在这里', grab:'有新的订单会显示在这里', accepted:'已接单的会显示在这里', in_progress:'进行中的会显示在这里', dispatched:'系统派单后会在这里显示' }
    }
  },
  computed: {
    pageTitle() { return this.titles[this.type] || '任务列表' },
    emptyIcon() { return this.emptyIcons[this.type] || '📋' },
    emptyTitle() { return this.emptyTitles[this.type] || '暂无数据' },
    emptyDesc() { return this.emptyDescs[this.type] || '' }
  },
  onLoad(query) { this.type = query.type || 'today'; uni.setNavigationBarTitle({ title: this.pageTitle }); this.loadData() },
  onPullDownRefresh() { this.loadData().then(() => uni.stopPullDownRefresh()) },
  methods: {
    statusTxt(s) { const m={pending:'待接单',dispatched:'已派单',accepted:'已接单',in_progress:'进行中',completed:'已完成',paid:'已付款',done:'已完成',cancelled:'已取消',CANCEL_PENDING:'待审核'}; return m[s]||s },
    goBack() { uni.navigateBack() },
    goDetail(id) { uni.navigateTo({ url:'/pages/orders/detail?id='+id }) },
    async loadData() {
      this.loading = true
      try {
        const user = uni.getStorageSync('user')
        if (!user) return uni.reLaunch({ url:'/pages/login/index' })
        const res = await api.getMyOrders(user.id)
        let list = (Array.isArray(res.data) ? res.data : res.data?.items) || []
        const _d=new Date(),_y=_d.getFullYear(),_m=String(_d.getMonth()+1).padStart(2,'0'),_dd=String(_d.getDate()).padStart(2,'0')
        const today = _y+'-'+_m+'-'+_dd
        const _td=new Date(Date.now()+864e5)
        const tomorrow = _td.getFullYear()+'-'+String(_td.getMonth()+1).padStart(2,'0')+'-'+String(_td.getDate()).padStart(2,'0')
        const ym = _y+'-'+_m
        if (this.type === 'today') list = list.filter(o => (o.appointment_time||'').startsWith(today))
        else if (this.type === 'tomorrow') list = list.filter(o => (o.appointment_time||'').startsWith(tomorrow))
        else if (this.type === 'pending') list = list.filter(o => o.status === 'CANCEL_PENDING')
        else if (this.type === 'month') list = list.filter(o => (o.status === 'completed' || o.status === 'done' || o.status === 'paid') && (o.completed_at||o.paid_at||'').startsWith(ym))
        else if (this.type === 'accepted') list = list.filter(o => o.status === 'accepted')
        else if (this.type === 'in_progress') list = list.filter(o => o.status === 'in_progress')
        else if (this.type === 'dispatched') list = list.filter(o => o.status === 'dispatched')
        else if (this.type === 'grab') { const uid = uni.getStorageSync('user')?.id; try { const r = await api.getNearbyOrders(uid); list = r.data || [] } catch(e){ list = [] } }
        this.orders = list
      } catch(e) { console.error(e); uni.showToast({ title:'加载失败', icon:'none' }) }
      finally { this.loading = false }
    }
  }
}
</script>

<style>
.page{background:var(--bg-page);min-height:100vh}
.header-bar{display:flex;align-items:center;justify-content:space-between;padding:var(--spacing-md);background:var(--bg-card);border-bottom:1px solid var(--border)}
.back-btn{font-size:var(--font-md);color:var(--primary);font-weight:500}
.title-txt{font-size:var(--font-lg);font-weight:600;color:var(--text-primary)}
.loading-state{padding:var(--spacing-lg);display:flex;flex-direction:column;gap:var(--spacing-sm)}
.empty-state{background:var(--bg-card);border-radius:var(--radius-lg);margin:var(--spacing-md);padding:60px 20px;text-align:center;box-shadow:var(--shadow-sm);border:1px dashed var(--border-strong)}
.empty-circle{width:64px;height:64px;border-radius:50%;background:var(--bg-fill);display:flex;align-items:center;justify-content:center;margin:0 auto var(--spacing-lg);font-size:28px}
.empty-title{font-size:var(--font-xl);font-weight:600;color:var(--text-primary);margin-bottom:var(--spacing-xs)}
.empty-desc{font-size:var(--font-base);color:var(--text-tertiary)}
.list{padding:var(--spacing-md)}
.task-card{background:var(--bg-card);border-radius:var(--radius-lg);padding:var(--spacing-lg);margin-bottom:var(--spacing-sm);border:1px solid var(--border);box-shadow:var(--shadow-sm);animation:fadeIn .3s ease}
.task-header{display:flex;justify-content:space-between;margin-bottom:6px;font-size:var(--font-sm)}
.task-time{color:var(--text-tertiary)}
.task-status{font-size:var(--font-sm);padding:2px 10px;border-radius:var(--radius-sm);font-weight:500;background:var(--bg-fill);color:var(--text-secondary)}
.task-status.in_progress{background:var(--warning-bg);color:#d48806}
.task-status.accepted{background:var(--primary-light);color:var(--primary)}
.task-status.completed,.task-status.done{background:var(--success-bg);color:var(--success)}
.task-status.CANCEL_PENDING{background:var(--warning-bg);color:#d48806}
.task-status.dispatched{background:var(--primary-light);color:var(--primary)}
.task-title{font-size:var(--font-md);font-weight:600;margin-bottom:4px;color:var(--text-primary);display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.task-cate{background:var(--bg-fill);padding:2px 8px;border-radius:var(--radius-sm);font-size:var(--font-sm);color:var(--text-tertiary)}
.task-addr{font-size:var(--font-sm);color:var(--text-secondary);margin:var(--spacing-sm) 0;background:var(--bg-page);padding:6px 8px;border-radius:var(--radius-sm);line-height:1.4}
.task-footer{display:flex;justify-content:space-between;align-items:center;margin-top:var(--spacing-sm);padding-top:var(--spacing-sm);border-top:1px solid var(--border);font-size:var(--font-sm)}
.task-customer{color:var(--text-secondary)}
.task-fee{color:var(--danger);font-weight:600}
@keyframes fadeIn{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
</style>
