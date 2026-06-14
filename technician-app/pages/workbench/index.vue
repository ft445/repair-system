<template>
  <view class="page">
    <!-- ===== 骨架屏 ===== -->
    <view v-if="loading" class="main-content">
      <view class="skeleton-card" style="border-radius:var(--radius-xl);padding:24px 20px;min-height:120px">
        <view class="skeleton-line w40"></view>
        <view class="skeleton-line w60 h48" style="margin:8px 0"></view>
        <view style="display:flex;gap:10px;margin-top:12px">
          <view class="skeleton-block" style="flex:1;height:50px"></view>
          <view class="skeleton-block" style="flex:1;height:50px"></view>
          <view class="skeleton-block" style="flex:1;height:50px"></view>
        </view>
      </view>
      <view class="skeleton-card" style="height:80px;display:flex;gap:8px;padding:12px">
        <view class="skeleton-block" style="flex:1;height:56px"></view>
        <view class="skeleton-block" style="flex:1;height:56px"></view>
        <view class="skeleton-block" style="flex:1;height:56px"></view>
        <view class="skeleton-block" style="flex:1;height:56px"></view>
      </view>
      <view class="skeleton-card" style="height:80px;display:flex;gap:8px;padding:12px">
        <view class="skeleton-block" style="flex:1;height:56px"></view>
        <view class="skeleton-block" style="flex:1;height:56px"></view>
        <view class="skeleton-block" style="flex:1;height:56px"></view>
        <view class="skeleton-block" style="flex:1;height:56px"></view>
      </view>
    </view>

    <view v-else class="main-content">
      <!-- ===== 头部：问候 + 打卡 ===== -->
      <view class="header">
        <view>
          <view class="header-top">
            <text class="h-greeting">{{ greeting }}</text>
            <view class="bell-wrap" @click="goNotifications">
              <text class="bell-icon">🔔</text>
              <view class="bell-badge" v-if="unreadCount > 0">{{ unreadCount > 99 ? '99+' : unreadCount }}</view>
            </view>
          </view>
          <text class="h-date">{{ todayStr }}</text>
        </view>
        <view :class="'clock-btn '+(clockedIn?'clocked-in':'')" @click="toggleClock">
          <view class="clock-inner">
            <view :class="'clock-dot '+(clockedIn?'dot-on':'')"></view>
            <text class="clock-text">{{ clockedIn?'已打卡':'上班打卡' }}</text>
          </view>
        </view>
      </view>

      <!-- ===== 收入卡 ===== -->
      <view class="income-card" @click="goTab('/pages/income/index')">
        <view class="ic-deco"></view>
        <view class="ic-top">
          <view>
            <text class="ic-label">今日收入</text>
            <text class="ic-amount">¥{{ todayEarn }}</text>
          </view>
          <view class="ic-badge">{{ clockedIn?'已接单':'未打卡' }}</view>
        </view>
        <view class="ic-bar">
          <view class="ic-item">
            <text class="ic-num">¥{{ monthEarn.toLocaleString() }}</text>
            <text class="ic-lbl">本月收入</text>
          </view>
          <view class="ic-vline"></view>
          <view class="ic-item">
            <text class="ic-num">{{ monthOrders }}</text>
            <text class="ic-lbl">本月工单</text>
          </view>
          <view class="ic-vline"></view>
          <view class="ic-item">
            <text class="ic-num">{{ stats.completed }}</text>
            <text class="ic-lbl">已完成</text>
          </view>
        </view>
      </view>

      <!-- ===== 工单状态 ===== -->
      <view class="section-hd">
        <text class="sh-title">📋 工单状态</text>
        <text class="sh-action" @click="goOrders()">全部 ›</text>
      </view>
      <view class="stat-grid">
        <view class="stat-card stat-pending" @click="openTasks('dispatched')">
          <text class="sc-num">{{ stats.pending }}</text>
          <text class="sc-label">待接单</text>
        </view>
        <view class="stat-card stat-accepted" @click="openTasks('accepted')">
          <text class="sc-num">{{ stats.accepted }}</text>
          <text class="sc-label">已接单</text>
        </view>
        <view class="stat-card stat-progress" @click="openTasks('in_progress')">
          <text class="sc-num">{{ stats.inProgress }}</text>
          <text class="sc-label">进行中</text>
        </view>
        <view class="stat-card stat-grab" @click="openTasks('grab')">
          <text class="sc-num" style="color:#ff4d4f">{{ nearbyCount }}</text>
          <text class="sc-label" style="color:#ff4d4f">抢单大厅</text>
        </view>
      </view>

      <!-- ===== 快速概览 ===== -->
      <view class="section-hd">
        <text class="sh-title">📊 快速概览</text>
        <text class="sh-action" @click="goOrders()">全部工单 ›</text>
      </view>
      <view class="overview-grid">
        <view class="ov-item ov-today" @click="openTasks('today')">
          <view class="ov-icon">📅</view>
          <text class="ov-num">{{ todayOrders.length }}</text>
          <text class="ov-lbl">今日上门</text>
        </view>
        <view class="ov-item ov-tomorrow" @click="openTasks('tomorrow')">
          <view class="ov-icon">📆</view>
          <text class="ov-num">{{ tomorrowOrders.length }}</text>
          <text class="ov-lbl">明日上门</text>
        </view>
        <view class="ov-item ov-audit" @click="openTasks('pending')">
          <view class="ov-icon">⏳</view>
          <text class="ov-num">{{ pendingCancelOrders.length }}</text>
          <text class="ov-lbl">待审核</text>
        </view>
        <view class="ov-item ov-month" @click="openTasks('month')">
          <view class="ov-icon">📊</view>
          <text class="ov-num">{{ monthOrders }}</text>
          <text class="ov-lbl">本月工单</text>
        </view>
      </view>

      <!-- ===== 快捷操作 ===== -->
      <view class="section-hd"><text class="sh-title">⚡ 快捷操作</text></view>
      <view class="action-grid">
        <view class="action-card" @click="scanCode">
          <view class="ac-icon ac-scan">📷</view>
          <text class="ac-label">扫单接单</text>
        </view>
        <view class="action-card" @click="callService">
          <view class="ac-icon ac-phone">📞</view>
          <text class="ac-label">联系客服</text>
        </view>
        <view class="action-card" @click="openTasks('today')">
          <view class="ac-icon ac-today">📋</view>
          <text class="ac-label">今日行程</text>
        </view>
        <view class="action-card" @click="jump('/pages/schedule/index')">
          <view class="ac-icon ac-schedule">📅</view>
          <text class="ac-label">工作日程</text>
        </view>
      </view>

      <!-- ===== 待审核提醒 ===== -->
      <view class="warn-bar" v-if="pendingCancelOrders.length" @click="goOrders()">
        <view class="warn-icon">!</view>
        <text class="warn-text">{{ pendingCancelOrders.length }} 个订单等待平台审核</text>
        <text class="warn-action">查看 ›</text>
      </view>

      <!-- ===== 今日上门 ===== -->
      <template v-if="todayOrders.length">
        <view class="section-hd">
          <text class="sh-title" style="color:var(--primary)">🔴 今日上门</text>
          <text class="sh-action">{{ todayOrders.length }}个 ›</text>
        </view>
        <view v-for="item in todayOrders" :key="item.id" class="order-card" @click="goDetail(item.id)">
          <view class="oc-left">
            <view class="oc-time-badge">{{ formatTimeSlot(item.appointment_time) }}</view>
          </view>
          <view class="oc-body">
            <view class="oc-top">
              <text class="oc-title">{{ item.service_item_name || '维修' }}</text>
              <text :class="'oc-status oc-' + item.status">{{ statusTxt(item.status) }}</text>
            </view>
            <text class="oc-addr">📍 {{ item.address?.slice(0,28) || '' }}</text>
            <view class="oc-footer">
              <text class="oc-customer">{{ item.customer_name || '客户' }}</text>
              <view class="oc-actions">
                <text class="oc-act" @click.stop="goDetail(item.id)">📞 联系</text>
                <text class="oc-act" @click.stop="openMap(item)">🗺️ 导航</text>
              </view>
            </view>
          </view>
        </view>
      </template>

      <!-- ===== 明日上门 ===== -->
      <template v-if="tomorrowOrders.length">
        <view class="section-hd">
          <text class="sh-title">📌 明日上门</text>
          <text class="sh-action">{{ tomorrowOrders.length }}个 ›</text>
        </view>
        <view v-for="item in tomorrowOrders" :key="item.id" class="order-card card-tomorrow" @click="goDetail(item.id)">
          <view class="oc-left">
            <view class="oc-time-badge tomorrow-badge">{{ formatTimeSlot(item.appointment_time) }}</view>
          </view>
          <view class="oc-body">
            <view class="oc-top">
              <text class="oc-title">{{ item.service_item_name || '维修' }}</text>
              <text class="oc-status oc-booked">已预约</text>
            </view>
            <text class="oc-addr">📍 {{ item.address?.slice(0,28) || '' }}</text>
            <view class="oc-footer">
              <text class="oc-customer">{{ item.customer_name || '客户' }}</text>
              <text class="oc-act" @click.stop="goDetail(item.id)">查看详情 ›</text>
            </view>
          </view>
        </view>
      </template>

      <!-- ===== 在途订单 ===== -->
      <template v-if="myOrders.length">
        <view class="section-hd">
          <text class="sh-title">🔄 在途订单</text>
          <text class="sh-action">{{ myOrders.length }}个 ›</text>
        </view>
        <view v-for="item in myOrders" :key="item.id" class="order-card" @click="goDetail(item.id)">
          <view class="oc-left">
            <view class="oc-time-badge route-badge">{{ (item.created_at||'').slice(5,10) }}</view>
          </view>
          <view class="oc-body">
            <view class="oc-top">
              <text class="oc-title">{{ item.service_item_name || '维修' }}</text>
              <text :class="'oc-status oc-' + item.status">{{ statusTxt(item.status) }}</text>
            </view>
            <text class="oc-addr">📍 {{ (item.customer_name||'客户')+' · '+(item.address||'').slice(0,22) }}</text>
            <text class="oc-order-no" v-if="item.order_no">#{{ item.order_no }}</text>
          </view>
        </view>
      </template>

      <!-- ===== 空状态提示 ===== -->
      <view v-if="!todayOrders.length && !tomorrowOrders.length && !myOrders.length" class="empty-section">
        <view class="empty-icon">🛠️</view>
        <text class="empty-title">暂无待办工单</text>
        <text class="empty-desc">当有新工单时会通知您</text>
      </view>

      <view class="bottom-spacer"></view>
    </view>
  </view>
</template>

<script>
import api from '../../api'
import wsService from '../../services/websocket'
export default {
  data() {
    return {
      user: null, todayEarn: 0, monthEarn: 0, monthOrders: 0, clockedIn: false, loading: true,
      stats: { pending: 0, accepted: 0, inProgress: 0, completed: 0 },
      myOrders: [], todayOrders: [], tomorrowOrders: [], pendingCancelOrders: [], cancelledOrders: [], bigOrders: 0, nearbyCount: 0,
      totalActiveOrders: 0, todayStr: '', greeting: '', unreadCount: 0,
      _hasActiveOrders: false,
    }
  },
  onShow() {
    this.user = uni.getStorageSync('user')
    if (!this.user) return uni.reLaunch({ url: '/pages/login/index' })
    this.loadData()
    this.loadUnreadCount()
    this.startSmartGps()
    this.checkPermissions()
    this.startWebSocketFallback()
    this.setupWsListeners()
  },
  onPullDownRefresh() { this.loadData().then(() => uni.stopPullDownRefresh()) },
  onUnload() { this._cleanup() },
  onHide() { this._cleanup() },
  methods: {
    formatTimeSlot(t) {
      if (!t || t.length < 16) return '尽快'
      const d = parseInt(t.slice(8,10)), h = parseInt(t.slice(11,13)), m = t.slice(14,16)
      return d+'日 '+h+':'+m
    },
    _cleanup() {
      if (this._pollTimer) { clearInterval(this._pollTimer); this._pollTimer = null }
      if (this._gpsTimer) { clearInterval(this._gpsTimer); this._gpsTimer = null }
    },
    statusTxt(s) { const m={pending:'待接单',dispatched:'已派单',accepted:'已接单',in_progress:'进行中',completed:'已完成',paid:'已付款',done:'已完成',cancelled:'已取消',CANCEL_PENDING:'待审核'}; return m[s]||s },
    async loadData() {
      try {
        const [res, nearbyRes] = await Promise.all([
          api.getMyOrders(this.user.id),
          api.getNearbyOrders(this.user?.id).catch(()=>({data:[]}))
        ])
        const orders = (Array.isArray(res.data) ? res.data : res.data?.items) || []
        this.nearbyCount = (nearbyRes.data||[]).length
        const s = { pending: 0, accepted: 0, inProgress: 0, completed: 0 }
        orders.forEach(o => {
          if (o.status === 'dispatched') s.pending++
          else if (o.status === 'accepted') s.accepted++
          else if (o.status === 'in_progress') s.inProgress++
          else if (o.status === 'completed' || o.status === 'done' || o.status === 'paid') s.completed++
        })
        this.stats = s
        this.totalActiveOrders = s.pending + s.accepted + s.inProgress
        this._hasActiveOrders = s.inProgress > 0
        const earnDone = orders.filter(o => (o.status === 'completed' || o.status === 'done' || o.status === 'paid') && o.total_fee)
        const countDone = orders.filter(o => o.status === 'completed' || o.status === 'done' || o.status === 'paid')
        this.todayEarn = earnDone.filter(o => (o.completed_at||o.paid_at||o.created_at||'').slice(0,10) === new Date().toISOString().slice(0,10)).reduce((s,o) => s + (o.total_fee||0), 0)
        const ym = new Date().toISOString().slice(0,7)
        const mDone = earnDone.filter(o => (o.completed_at||o.paid_at||'').startsWith(ym))
        const mCount = countDone.filter(o => (o.completed_at||o.paid_at||'').startsWith(ym))
        this.monthEarn = mDone.reduce((s,o) => s + (o.total_fee||0), 0)
        this.monthOrders = mCount.length
        this.myOrders = orders.filter(o => o.status === 'accepted' || o.status === 'in_progress' || o.status === 'dispatched')
        const d = new Date()
        const todayStr = d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')
        const tmA=new Date(Date.now()+864e5)
        const tomorrowStr = tmA.getFullYear()+'-'+String(tmA.getMonth()+1).padStart(2,'0')+'-'+String(tmA.getDate()).padStart(2,'0')
        this.todayOrders = orders.filter(o => (o.status === 'accepted' || o.status === 'in_progress') && (o.appointment_time||'').startsWith(todayStr))
        this.tomorrowOrders = orders.filter(o => o.status === 'accepted' && (o.appointment_time||'').startsWith(tomorrowStr))
        this.pendingCancelOrders = orders.filter(o => o.status === 'CANCEL_PENDING')
        this.cancelledOrders = orders.filter(o => o.status === 'cancelled')
        this.bigOrders = orders.filter(o => (o.status === 'accepted' || o.status === 'in_progress' || o.status === 'dispatched') && (o.total_fee||0) >= 200).length
        const weekdays = ['日','一','二','三','四','五','六']
        this.todayStr = d.getFullYear()+'年'+(d.getMonth()+1)+'月'+d.getDate()+'日 周'+weekdays[d.getDay()]
        // 问候语
        const h = d.getHours()
        const name = this.user?.name || '师傅'
        if (h < 6) this.greeting = '夜深了，'+name
        else if (h < 9) this.greeting = '早上好，'+name
        else if (h < 12) this.greeting = '上午好，'+name
        else if (h < 14) this.greeting = '中午好，'+name
        else if (h < 18) this.greeting = '下午好，'+name
        else this.greeting = '晚上好，'+name
      } catch(e) { console.error(e) }
      finally { this.loading = false }
    },
    toggleClock() {
      if (this.clockedIn) {
        api.clockOut(this.user.id).then(() => {
          this.clockedIn = false
          uni.showToast({ title:'已下班' })
          this._updateGpsInterval()
        }).catch(e => uni.showToast({ title:e.message||'打卡失败', icon:'none' }))
      } else {
        uni.showModal({ title:'上班打卡', content:'确认开始今日工作？', success:(r)=>{
          if(r.confirm) api.clockIn(this.user.id).then(() => {
            this.clockedIn = true
            uni.showToast({ title:'打卡成功' })
            this._updateGpsInterval()
          }).catch(e => uni.showToast({ title:e.message||'打卡失败', icon:'none' }))
        }})
      }
    },
    setupWsListeners() {
      if (this._wsReady) return
      this._wsReady = true
      wsService.onOrderUpdate(() => { this.loadData() })
      wsService.onNotification(() => { this.loadUnreadCount() })
      uni.$on('orderUpdated', () => { this.loadData() })
    },
    startWebSocketFallback() {
      if (this._pollTimer) return
      this._pollTimer = setInterval(() => {
        if (wsService.isConnected()) return
        api.getMyOrders(this.user.id).then(res => {
          const list = res.data || []
          this.stats.pending = list.filter(o => o.status === 'dispatched').length
        }).catch(()=>{})
      }, 60000)
    },
    startSmartGps() {
      if (this._gpsTimer) return
      const doReport = () => {
        uni.getLocation({
          type: 'gcj02',
          success: (r) => { api.updateLocation(r.latitude, r.longitude, this.user?.id).catch(()=>{}) },
          fail: () => {}
        })
      }
      doReport()
      this._updateGpsInterval = () => {
        if (this._gpsTimer) { clearInterval(this._gpsTimer); this._gpsTimer = null }
        if (!this.clockedIn) return
        this._gpsTimer = setInterval(doReport, this._hasActiveOrders ? 60000 : 300000)
      }
      this._updateGpsInterval()
    },
    async loadUnreadCount() {
      try {
        const res = await api.getUnreadCount()
        this.unreadCount = res.data?.count || 0
      } catch(e) {}
    },
    scanCode() {
      if (typeof uni !== 'undefined' && uni.scanCode) {
        uni.scanCode({
          success: (r) => {
            const code = r.result || ''
            if (/^\d+$/.test(code)) { uni.navigateTo({ url: '/pages/orders/detail?id=' + code }); return }
            if (/^(WX|wo)/i.test(code)) {
              uni.showToast({ title:'正在查找工单...', icon:'none' })
              api.getMyOrders(this.user?.id).then(res => {
                const orders = (Array.isArray(res.data) ? res.data : res.data?.items) || []
                const found = orders.find(o => (o.order_no||'').toUpperCase() === code.toUpperCase())
                if (found) uni.navigateTo({ url: '/pages/orders/detail?id=' + found.id })
                else uni.showToast({ title:'未找到该工单', icon:'none' })
              }).catch(() => uni.showToast({ title:'查找失败', icon:'none' }))
              return
            }
            uni.showToast({ title:'扫码: '+code.slice(0,20), icon:'none' })
          },
          fail: () => { this._manualCodeInput() }
        })
      } else { this._manualCodeInput() }
    },
    _manualCodeInput() {
      uni.showModal({
        title: '输入工单号', content: '当前环境不支持扫码，请手动输入工单ID',
        editable: true, placeholderText: '输入工单号',
        success: (r) => {
          if (r.confirm && r.content) {
            const val = r.content.trim()
            if (/^\d+$/.test(val)) uni.navigateTo({ url: '/pages/orders/detail?id=' + val })
            else uni.showToast({ title:'请输入有效的工单号', icon:'none' })
          }
        }
      })
    },
    callService() {
      const phone = uni.getStorageSync('servicePhone') || '4000000000'
      uni.showModal({ title:'联系客服', content:'拨打客服热线？', success:(r)=>{ if(r.confirm) uni.makePhoneCall({ phoneNumber: phone }) }})
    },
    goNotifications() { uni.navigateTo({ url: '/pages/notifications/index' }) },
    openMap(item) {
      if (item.latitude && item.longitude) { uni.openLocation({ latitude: parseFloat(item.latitude), longitude: parseFloat(item.longitude) }) }
      else { uni.showToast({ title:'暂无位置信息', icon:'none' }) }
    },
    goOrders(s) { if(s)uni.setStorageSync('orderFilter',s); uni.switchTab({ url:'/pages/orders/index' }) },
    goDetail(id) { uni.navigateTo({ url:'/pages/orders/detail?id='+id }) },
    goTab(url) { uni.switchTab({ url }) },
    openTasks(type) { uni.navigateTo({ url:'/pages/tasks/index?type='+type }) },
    jump(url) { uni.navigateTo({ url }) },
    checkPermissions() {
      if (typeof plus !== 'undefined') {
        try {
          plus.android.requestPermissions(['android.permission.CAMERA','android.permission.ACCESS_FINE_LOCATION','android.permission.CALL_PHONE','android.permission.RECORD_AUDIO'], function(e) {
            var denied = (e.deniedAlways||[]).concat(e.deniedPresent||[])
            if (denied.length) uni.showModal({ title:'需要权限', content:'请允许相机、定位权限', confirmText:'去设置', success:(r)=>{if(r.confirm)plus.runtime.openURL('app-settings://')} })
          })
        } catch(e) {}
      }
    }
  }
}
</script>

<style>
/* ========== Layout ========== */
.page{background:var(--bg-page);min-height:100vh}
.main-content{max-width:450px;margin:0 auto;padding:0 var(--spacing-lg) 0;animation:fadeIn .25s ease}
.bottom-spacer{height:40px}

/* ========== Header ========== */
.header{display:flex;justify-content:space-between;align-items:flex-start;padding:var(--spacing-lg) 0;animation:fadeIn .3s ease}
.header-top{display:flex;align-items:center;gap:8px}
.h-greeting{font-size:22px;font-weight:700;color:var(--text-primary);letter-spacing:-0.3px;line-height:1.3}
.h-date{font-size:var(--font-sm);color:var(--text-tertiary);margin-top:2px;display:block}

/* Clock Button */
.clock-btn{border-radius:var(--radius-round);background:var(--bg-card);border:1.5px solid var(--border);padding:3px;min-height:34px;transition:all .25s;flex-shrink:0}
.clock-btn:active{transform:scale(0.93)}
.clock-btn.clocked-in{border-color:var(--success);background:var(--success-bg)}
.clock-inner{display:flex;align-items:center;gap:5px;padding:0 14px 0 10px}
.clock-dot{width:7px;height:7px;border-radius:50%;background:var(--text-tertiary);transition:all .25s}
.clock-dot.dot-on{background:var(--success);box-shadow:0 0 6px rgba(82,196,26,.5)}
.clock-text{font-size:var(--font-sm);font-weight:600;color:var(--text-secondary)}
.clock-btn.clocked-in .clock-text{color:var(--success)}

/* ========== Income Card ========== */
.income-card{background:linear-gradient(135deg,#E67A2E,#d4681e);border-radius:var(--radius-xl);padding:var(--spacing-xl) var(--spacing-xl);margin-bottom:var(--spacing-md);color:#fff;position:relative;overflow:hidden;box-shadow:0 4px 20px rgba(230,122,46,0.25)}
.income-card:active{opacity:.95}
.ic-deco{position:absolute;top:-40px;right:-30px;width:120px;height:120px;border-radius:50%;background:rgba(255,255,255,.07)}
.ic-deco::after{content:'';position:absolute;bottom:-30px;left:-50px;width:100px;height:100px;border-radius:50%;background:rgba(255,255,255,.05)}
.ic-top{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:var(--spacing-md);position:relative}
.ic-label{font-size:var(--font-base);opacity:.8}
.ic-amount{font-size:38px;font-weight:700;letter-spacing:-1px;line-height:1.1}
.ic-badge{font-size:var(--font-sm);padding:4px 12px;border-radius:var(--radius-round);background:rgba(255,255,255,.15)}
.ic-bar{display:flex;background:rgba(255,255,255,.1);border-radius:var(--radius-md);padding:12px 8px;backdrop-filter:blur(6px)}
.ic-item{flex:1;text-align:center}
.ic-num{font-size:var(--font-xl);font-weight:700;display:block}
.ic-lbl{font-size:var(--font-sm);opacity:.75;margin-top:2px}
.ic-vline{width:1px;background:rgba(255,255,255,.15);margin:4px 0}

/* ========== Section Headers ========== */
.section-hd{display:flex;justify-content:space-between;align-items:center;margin:var(--spacing-md) 0 var(--spacing-sm)}
.sh-title{font-size:var(--font-lg);font-weight:600;color:var(--text-primary)}
.sh-action{font-size:var(--font-sm);color:var(--text-tertiary);padding:4px 8px}

/* ========== Status Grid ========== */
.stat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:var(--spacing-sm);margin-bottom:var(--spacing-md)}
.stat-card{background:var(--bg-card);border-radius:var(--radius-md);padding:var(--spacing-md) var(--spacing-xs);text-align:center;box-shadow:var(--shadow-sm);border:1px solid var(--border);transition:all .15s}
.stat-card:active{transform:scale(0.95)}
.sc-num{font-size:var(--font-3xl);font-weight:700;color:var(--text-primary);display:block;line-height:1.2}
.sc-label{font-size:var(--font-sm);color:var(--text-tertiary);margin-top:4px;display:block}

/* ========== Overview Grid ========== */
.overview-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:var(--spacing-sm);margin-bottom:var(--spacing-md)}
.ov-item{background:var(--bg-card);border-radius:var(--radius-md);padding:var(--spacing-md) var(--spacing-xs);text-align:center;box-shadow:var(--shadow-sm);border:1px solid var(--border);transition:all .15s}
.ov-item:active{transform:scale(0.93)}
.ov-icon{font-size:20px;margin-bottom:4px;display:block}
.ov-num{font-size:var(--font-xl);font-weight:700;color:var(--text-primary);display:block;line-height:1.2}
.ov-lbl{font-size:11px;color:var(--text-tertiary);margin-top:2px;display:block}

/* ========== Action Grid ========== */
.action-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:var(--spacing-sm);margin-bottom:var(--spacing-md)}
.action-card{background:var(--bg-card);border-radius:var(--radius-md);padding:var(--spacing-md) var(--spacing-xs);text-align:center;box-shadow:var(--shadow-sm);border:1px solid var(--border);transition:all .15s}
.action-card:active{transform:scale(0.93)}
.ac-icon{width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 6px;font-size:18px}
.ac-scan{background:linear-gradient(135deg,#667eea,#764ba2)}
.ac-phone{background:linear-gradient(135deg,#43e97b,#38f9d7)}
.ac-today{background:var(--primary-gradient)}
.ac-schedule{background:linear-gradient(135deg,#f093fb,#f5576c)}
.ac-label{font-size:var(--font-sm);color:var(--text-secondary);display:block}

/* ========== Warn Bar ========== */
.warn-bar{display:flex;align-items:center;gap:var(--spacing-sm);background:var(--warning-bg);border-radius:var(--radius-lg);padding:var(--spacing-md) var(--spacing-lg);margin-bottom:var(--spacing-md);border-left:3px solid var(--warning)}
.warn-icon{width:20px;height:20px;border-radius:50%;background:var(--warning);color:#fff;text-align:center;line-height:20px;font-size:13px;font-weight:700;flex-shrink:0}
.warn-text{flex:1;font-size:var(--font-base);color:#b45f06;line-height:1.4}
.warn-action{font-size:var(--font-sm);color:var(--primary);font-weight:500}

/* ========== Order Cards ========== */
.order-card{background:var(--bg-card);border-radius:var(--radius-lg);margin-bottom:var(--spacing-sm);padding:var(--spacing-lg);display:flex;gap:var(--spacing-md);box-shadow:var(--shadow-sm);border:1px solid var(--border);transition:all .15s;animation:fadeIn .3s ease}
.order-card:active{background:var(--bg-fill)}
.oc-left{flex-shrink:0}
.oc-time-badge{width:50px;padding:8px 0;background:var(--primary-light);border-radius:var(--radius-sm);text-align:center;font-size:var(--font-sm);font-weight:600;color:var(--primary);line-height:1.3}
.tomorrow-badge{background:var(--info-bg);color:var(--info)}
.route-badge{background:var(--bg-fill);color:var(--text-secondary);font-size:13px}
.oc-body{flex:1;min-width:0}
.oc-top{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:4px}
.oc-title{font-size:var(--font-md);font-weight:600;color:var(--text-primary);flex:1}
.oc-status{font-size:11px;padding:2px 8px;border-radius:var(--radius-round);background:#f0f2f5;color:var(--text-secondary);font-weight:500;white-space:nowrap}
.oc-status.in_progress{background:#fff3e0;color:var(--primary)}
.oc-status.accepted,.oc-status.booked{background:var(--info-bg);color:var(--info)}
.oc-status.dispatched{background:var(--warning-bg);color:#d48806}
.oc-status.CANCEL_PENDING{background:#fce4ec;color:var(--danger)}
.oc-addr{font-size:var(--font-sm);color:var(--text-tertiary);display:block;margin-bottom:6px;line-height:1.4}
.oc-order-no{font-size:11px;color:var(--text-tertiary)}
.oc-footer{display:flex;justify-content:space-between;align-items:center;margin-top:4px;padding-top:6px;border-top:1px solid var(--border)}
.oc-customer{font-size:var(--font-sm);color:var(--text-secondary);font-weight:500}
.oc-actions{display:flex;gap:var(--spacing-sm)}
.oc-act{font-size:var(--font-sm);color:var(--primary)}
.card-tomorrow{border-left:3px solid var(--info);opacity:.9}

/* ========== Empty State ========== */
.empty-section{background:var(--bg-card);border-radius:var(--radius-xl);padding:50px 20px;text-align:center;margin:var(--spacing-lg) 0;border:1.5px dashed var(--border-strong)}
.empty-icon{font-size:40px;margin-bottom:var(--spacing-md)}
.empty-title{font-size:var(--font-xl);font-weight:600;color:var(--text-primary);margin-bottom:var(--spacing-xs)}
.empty-desc{font-size:var(--font-base);color:var(--text-tertiary)}

/* ========== Notifications ========== */
.bell-wrap{position:relative;padding:2px}
.bell-icon{font-size:20px;line-height:1}
.bell-badge{position:absolute;top:-6px;right:-8px;background:var(--danger);color:#fff;font-size:9px;font-weight:700;min-width:15px;height:15px;line-height:15px;text-align:center;border-radius:7px;padding:0 4px;border:1.5px solid var(--bg-page)}

@keyframes fadeIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
</style>
