<template>
  <div class="page">
    <!-- ===== 骨架屏 ===== -->
    <div v-if="loading" class="main-content">
      <div class="skeleton-card" style="border-radius:var(--radius-xl);padding:24px 20px;min-height:120px">
        <div class="skeleton-line w40"></div>
        <div class="skeleton-line w60 h48" style="margin:8px 0"></div>
        <div style="display:flex;gap:10px;margin-top:12px">
          <div class="skeleton-block" style="flex:1;height:50px"></div>
          <div class="skeleton-block" style="flex:1;height:50px"></div>
          <div class="skeleton-block" style="flex:1;height:50px"></div>
        </div>
      </div>
      <div class="skeleton-card" style="height:80px;display:flex;gap:8px;padding:12px">
        <div class="skeleton-block" style="flex:1;height:56px"></div>
        <div class="skeleton-block" style="flex:1;height:56px"></div>
        <div class="skeleton-block" style="flex:1;height:56px"></div>
        <div class="skeleton-block" style="flex:1;height:56px"></div>
      </div>
    </div>

    <div v-else class="main-content">
      <!-- ===== 头部：问候 + 打卡 ===== -->
      <div class="header">
        <div>
          <div class="header-top">
            <span class="h-greeting">{{ greeting }}</span>
            <div class="bell-wrap" @click="goNotifications">
              <span class="bell-icon">🔔</span>
              <div class="bell-badge" v-if="unreadCount > 0">{{ unreadCount > 99 ? '99+' : unreadCount }}</div>
            </div>
          </div>
          <span class="h-date">{{ todayStr }}</span>
        </div>
        <div :class="'clock-btn '+(clockedIn?'clocked-in':'')" @click="toggleClock">
          <div class="clock-inner">
            <div :class="'clock-dot '+(clockedIn?'dot-on':'')"></div>
            <span class="clock-text">{{ clockedIn?'已打卡':'上班打卡' }}</span>
          </div>
        </div>
      </div>

      <!-- ===== 收入卡 ===== -->
      <div class="income-card" @click="goTab('/pages/income/index')">
        <div class="ic-deco"></div>
        <div class="ic-top">
          <div>
            <span class="ic-label">今日收入</span>
            <span class="ic-amount">¥{{ todayEarn }}</span>
          </div>
          <div class="ic-badge">{{ clockedIn?'已接单':'未打卡' }}</div>
        </div>
        <div class="ic-bar">
          <div class="ic-item">
            <span class="ic-num">¥{{ monthEarn.toLocaleString() }}</span>
            <span class="ic-lbl">本月收入</span>
          </div>
          <div class="ic-vline"></div>
          <div class="ic-item">
            <span class="ic-num">{{ monthOrders }}</span>
            <span class="ic-lbl">本月工单</span>
          </div>
          <div class="ic-vline"></div>
          <div class="ic-item">
            <span class="ic-num">{{ stats.completed }}</span>
            <span class="ic-lbl">已完成</span>
          </div>
        </div>
      </div>

      <!-- ===== 工单状态 ===== -->
      <div class="section-hd">
        <span class="sh-title">📋 工单状态</span>
        <span class="sh-action" @click="goOrders()">全部 ›</span>
      </div>
      <div class="stat-grid">
        <div class="stat-card" @click="openTasks('dispatched')">
          <span class="sc-num">{{ stats.pending }}</span>
          <span class="sc-label">待接单</span>
        </div>
        <div class="stat-card" @click="openTasks('accepted')">
          <span class="sc-num">{{ stats.accepted }}</span>
          <span class="sc-label">已接单</span>
        </div>
        <div class="stat-card" @click="openTasks('in_progress')">
          <span class="sc-num">{{ stats.inProgress }}</span>
          <span class="sc-label">进行中</span>
        </div>
        <div class="stat-card" @click="openTasks('grab')">
          <span class="sc-num" style="color:#ff4d4f">{{ nearbyCount }}</span>
          <span class="sc-label" style="color:#ff4d4f">抢单大厅</span>
        </div>
      </div>

      <!-- ===== 快捷概览 ===== -->
      <div class="section-hd">
        <span class="sh-title">📊 快捷概览</span>
        <span class="sh-action" @click="goOrders()">全部工单 ›</span>
      </div>
      <div class="stat-grid">
        <div class="stat-card" @click="openTasks('today')">
          <span class="sc-num">{{ todayCount }}</span>
          <span class="sc-label">今日上门</span>
        </div>
        <div class="stat-card" @click="openTasks('tomorrow')">
          <span class="sc-num">{{ tomorrowCount }}</span>
          <span class="sc-label">明日上门</span>
        </div>
        <div class="stat-card" @click="openTasks('pending')">
          <span class="sc-num">{{ pendingCancelOrders.length }}</span>
          <span class="sc-label">待审核</span>
        </div>
        <div class="stat-card" @click="openTasks('month')">
          <span class="sc-num">{{ monthOrders }}</span>
          <span class="sc-label">本月工单</span>
        </div>
      </div>

      <!-- ===== 快捷操作 ===== -->
      <div class="section-hd"><span class="sh-title">⚡ 快捷操作</span></div>
      <div class="stat-grid">
        <div class="stat-card" @click="scanCode">
          <div class="sc-icon">📷</div>
          <span class="sc-label">扫单接单</span>
        </div>
        <div class="stat-card" @click="callService">
          <div class="sc-icon">📞</div>
          <span class="sc-label">联系客服</span>
        </div>
        <div class="stat-card" @click="openTasks('today')">
          <div class="sc-icon">📋</div>
          <span class="sc-label">今日行程</span>
        </div>
        <div class="stat-card" @click="jump('/pages/schedule/index')">
          <div class="sc-icon">📅</div>
          <span class="sc-label">工作日程</span>
        </div>
      </div>

      <!-- ===== 待审核提醒 ===== -->
      <div class="warn-bar" v-if="pendingCancelOrders.length" @click="goOrders()">
        <div class="warn-icon">!</div>
        <span class="warn-text">{{ pendingCancelOrders.length }} 个订单等待平台审核</span>
        <span class="warn-action">查看 ›</span>
      </div>

      <!-- ===== 按日期分组的工单列表（横向滚动） ===== -->
      <template v-if="dateGroups.length">
        <div v-for="(group, gi) in dateGroups" :key="gi" class="date-group">
          <!-- 日期头 -->
          <div class="section-hd">
            <span class="sh-title">{{ group.label }}</span>
            <span class="sh-action">{{ group.orders.length }}个 ›</span>
          </div>
          <!-- 横向滚动卡片容器 — 【修复1：flex + overflow-x:auto + nowrap】 -->
          <div class="order-scroll">
            <div v-for="item in group.orders" :key="item.id" class="h-order-card" @click="goDetail(item.id)">
              <div class="hoc-top">
                <div class="hoc-time">
                  <span class="hoc-time-num">{{ timeNum(item.appointment_time) }}</span>
                  <span class="hoc-time-unit">{{ timeUnit(item.appointment_time) }}</span>
                </div>
                <span :class="'hoc-badge ' + item.status">{{ statusTxt(item.status) }}</span>
              </div>
              <div class="hoc-title">{{ item.service_item_name || '维修' }}</div>
              <div class="hoc-addr">📍 {{ item.address?.slice(0, 20) || '地址待确认' }}</div>
              <div class="hoc-footer">
                <span class="hoc-customer">{{ item.customer_name || '客户' }}</span>
                <span v-if="item.total_fee" class="hoc-fee">¥{{ item.total_fee }}</span>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- ===== 空状态 ===== -->
      <div v-if="!dateGroups.length && !loading" class="empty-section">
        <div class="empty-icon">🛠️</div>
        <span class="empty-title">暂无待办工单</span>
        <span class="empty-desc">当有新工单时会通知您</span>
      </div>

      <div class="bottom-spacer"></div>
    </div>
  </div>
</template>

<script>
import api from '../../api'
import wsService from '../../services/websocket'
export default {
  data() {
    return {
      user: null,
      todayEarn: 0,
      monthEarn: 0,
      monthOrders: 0,
      clockedIn: false,
      loading: true,
      stats: { pending: 0, accepted: 0, inProgress: 0, completed: 0 },
      // 【修复2】统一用 dateGroups 替代三个分散数组
      dateGroups: [],
      pendingCancelOrders: [],
      nearbyCount: 0,
      todayCount: 0,
      tomorrowCount: 0,
      todayStr: '',
      greeting: '',
      unreadCount: 0,
      _hasActiveOrders: false,
      // 【修复3】请求计数器防止竞态
      _reqId: 0,
    }
  },
  onShow() {
    this.user = uni.getStorageSync('user')
    if (!this.user) return uni.reLaunch({ url: '/pages/login/index' })
    // 【修复3】每次 onShow 自增 reqId，旧请求的响应被忽略
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
    /* ========== 工具函数 ========== */
    timeNum(t) {
      if (!t || t.length < 16) return '--'
      return t.slice(11, 16)
    },
    timeUnit(t) {
      if (!t || t.length < 16) return ''
      const d = parseInt(t.slice(8, 10))
      return d + '日'
    },
    statusTxt(s) {
      const m = { pending: '待接单', dispatched: '已派单', accepted: '已接单', in_progress: '进行中', completed: '已完成', paid: '已付款', done: '已完成', cancelled: '已取消', CANCEL_PENDING: '待审核' }
      return m[s] || s
    },
    _cleanup() {
      if (this._pollTimer) { clearInterval(this._pollTimer); this._pollTimer = null }
      if (this._gpsTimer) { clearInterval(this._gpsTimer); this._gpsTimer = null }
    },

    /* ========== 【修复2】按日期分组 + 过滤 0 元测试单 ========== */
    groupOrdersByDate(orders) {
      // 过滤 0 元测试单（total_fee 为空或为 0）
      const valid = orders.filter(o => o.total_fee && Number(o.total_fee) > 0)

      if (!valid.length) return []

      // 按 appointment_time 的日期分组
      const groups = {}
      valid.forEach(o => {
        const dateKey = (o.appointment_time || '').slice(0, 10) // "2026-06-15"
        if (!dateKey) {
          // 无预约时间的归入"待安排"
          const key = '_unscheduled'
          if (!groups[key]) groups[key] = []
          groups[key].push(o)
          return
        }
        if (!groups[dateKey]) groups[dateKey] = []
        groups[dateKey].push(o)
      })

      // 转为数组并排序（日期升序 = 最早的在前面）
      const now = new Date()
      const todayStr = now.toISOString().slice(0, 10)
      const tomorrowTs = Date.now() + 86400000
      const yesterdayTs = Date.now() - 86400000

      const result = []
      for (const [dateKey, orderList] of Object.entries(groups)) {
        if (dateKey === '_unscheduled') continue // 待安排单独处理

        let label = ''
        if (dateKey === todayStr) label = '🔴 今日上门'
        else if (dateKey === new Date(tomorrowTs).toISOString().slice(0, 10)) label = '📌 明日上门'
        else {
          const d = new Date(dateKey + 'T00:00:00')
          const diffDays = Math.round((d - now) / 86400000)
          if (diffDays > 1) label = `📆 ${parseInt(dateKey.slice(5, 7))}月${parseInt(dateKey.slice(8, 10))}日 (${diffDays}天后)`
          else if (diffDays === 1) label = '📌 明日上门'
          else if (diffDays === 0) label = '🔴 今日上门'
          else if (diffDays === -1) label = '🕐 昨日'
          else label = `🕐 ${parseInt(dateKey.slice(5, 7))}月${parseInt(dateKey.slice(8, 10))}日`
        }

        result.push({
          dateKey,
          label,
          orders: orderList.sort((a, b) => ((a.appointment_time || '') > (b.appointment_time || '') ? 1 : -1))
        })
      }

      // 按日期排序（升序）
      result.sort((a, b) => a.dateKey.localeCompare(b.dateKey))

      // 计算 today/tomorrow 计数
      this.todayCount = result.filter(g => g.dateKey === todayStr).reduce((s, g) => s + g.orders.length, 0)
      this.tomorrowCount = result.filter(g => g.dateKey === new Date(tomorrowTs).toISOString().slice(0, 10)).reduce((s, g) => s + g.orders.length, 0)

      return result
    },

    /* ========== 数据加载 ========== */
    async loadData() {
      // 【修复3】请求计数器+1，旧请求的响应到达时会被忽略
      const reqId = ++this._reqId

      // 【修复3】先清空旧数据
      this.dateGroups = []
      this.pendingCancelOrders = []
      this.stats = { pending: 0, accepted: 0, inProgress: 0, completed: 0 }

      try {
        const [res, nearbyRes] = await Promise.all([
          api.getMyOrders(this.user.id),
          api.getNearbyOrders(this.user?.id).catch(() => ({ data: [] }))
        ])
        // 如果已经不是最新请求，丢弃结果
        if (reqId !== this._reqId) return

        const orders = (Array.isArray(res.data) ? res.data : res.data?.items) || []
        this.nearbyCount = (nearbyRes.data || []).length

        // 统计状态
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

        // 收入计算
        const earnDone = orders.filter(o => (o.status === 'completed' || o.status === 'done' || o.status === 'paid') && o.total_fee)
        const countDone = orders.filter(o => o.status === 'completed' || o.status === 'done' || o.status === 'paid')
        this.todayEarn = earnDone.filter(o => (o.completed_at || o.paid_at || o.created_at || '').slice(0, 10) === new Date().toISOString().slice(0, 10))
          .reduce((sum, o) => sum + (o.total_fee || 0), 0)
        const ym = new Date().toISOString().slice(0, 7)
        this.monthEarn = earnDone.filter(o => (o.completed_at || o.paid_at || '').startsWith(ym))
          .reduce((sum, o) => sum + (o.total_fee || 0), 0)
        this.monthOrders = countDone.filter(o => (o.completed_at || o.paid_at || '').startsWith(ym)).length

        // 【修复2】按日期分组并过滤 0 元单
        this.dateGroups = this.groupOrdersByDate(orders)

        // 待审核
        this.pendingCancelOrders = orders.filter(o => o.status === 'CANCEL_PENDING')

        // 日期和问候
        const d = new Date()
        const weekdays = ['日', '一', '二', '三', '四', '五', '六']
        this.todayStr = d.getFullYear() + '年' + (d.getMonth() + 1) + '月' + d.getDate() + '日 周' + weekdays[d.getDay()]
        const h = d.getHours()
        const name = this.user?.name || '师傅'
        if (h < 6) this.greeting = '夜深了，' + name
        else if (h < 9) this.greeting = '早上好，' + name
        else if (h < 12) this.greeting = '上午好，' + name
        else if (h < 14) this.greeting = '中午好，' + name
        else if (h < 18) this.greeting = '下午好，' + name
        else this.greeting = '晚上好，' + name
      } catch (e) { console.error(e) }
      finally {
        if (reqId === this._reqId) this.loading = false
      }
    },

    /* ===== 打卡 ===== */
    toggleClock() {
      if (this.clockedIn) {
        api.clockOut(this.user.id).then(() => {
          this.clockedIn = false
          uni.showToast({ title: '已下班' })
          this._updateGpsInterval()
        }).catch(e => uni.showToast({ title: e.message || '打卡失败', icon: 'none' }))
      } else {
        uni.showModal({
          title: '上班打卡', content: '确认开始今日工作？', success: (r) => {
            if (r.confirm) api.clockIn(this.user.id).then(() => {
              this.clockedIn = true
              uni.showToast({ title: '打卡成功' })
              this._updateGpsInterval()
            }).catch(e => uni.showToast({ title: e.message || '打卡失败', icon: 'none' }))
          }
        })
      }
    },

    /* ===== WebSocket 监听 ===== */
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
        }).catch(() => { })
      }, 60000)
    },
    startSmartGps() {
      if (this._gpsTimer) return
      const doReport = () => {
        uni.getLocation({
          type: 'gcj02',
          success: (r) => { api.updateLocation(r.latitude, r.longitude, this.user?.id).catch(() => { }) },
          fail: () => { }
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

    /* ===== 未读数 ===== */
    async loadUnreadCount() {
      try {
        const res = await api.getUnreadCount()
        this.unreadCount = res.data?.count || 0
      } catch (e) { }
    },

    /* ===== 操作 ===== */
    scanCode() {
      if (typeof uni !== 'undefined' && uni.scanCode) {
        uni.scanCode({
          success: (r) => {
            const code = r.result || ''
            if (/^\d+$/.test(code)) { uni.navigateTo({ url: '/pages/orders/detail?id=' + code }); return }
            if (/^(WX|wo)/i.test(code)) {
              uni.showToast({ title: '正在查找工单...', icon: 'none' })
              api.getMyOrders(this.user?.id).then(res => {
                const orders = (Array.isArray(res.data) ? res.data : res.data?.items) || []
                const found = orders.find(o => (o.order_no || '').toUpperCase() === code.toUpperCase())
                if (found) uni.navigateTo({ url: '/pages/orders/detail?id=' + found.id })
                else uni.showToast({ title: '未找到该工单', icon: 'none' })
              }).catch(() => uni.showToast({ title: '查找失败', icon: 'none' }))
              return
            }
            uni.showToast({ title: '扫码: ' + code.slice(0, 20), icon: 'none' })
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
            else uni.showToast({ title: '请输入有效的工单号', icon: 'none' })
          }
        }
      })
    },
    callService() {
      const phone = uni.getStorageSync('servicePhone') || '4000000000'
      uni.showModal({ title: '联系客服', content: '拨打客服热线？', success: (r) => { if (r.confirm) uni.makePhoneCall({ phoneNumber: phone }) } })
    },
    goNotifications() { uni.navigateTo({ url: '/pages/notifications/index' }) },
    openMap(item) {
      if (item.latitude && item.longitude) { uni.openLocation({ latitude: parseFloat(item.latitude), longitude: parseFloat(item.longitude) }) }
      else { uni.showToast({ title: '暂无位置信息', icon: 'none' }) }
    },
    goOrders(s) { if (s) uni.setStorageSync('orderFilter', s); uni.switchTab({ url: '/pages/orders/index' }) },
    goDetail(id) { uni.navigateTo({ url: '/pages/orders/detail?id=' + id }) },
    goTab(url) { uni.switchTab({ url }) },
    openTasks(type) { uni.navigateTo({ url: '/pages/tasks/index?type=' + type }) },
    jump(url) { uni.navigateTo({ url }) },
    checkPermissions() {
      if (typeof plus !== 'undefined') {
        try {
          plus.android.requestPermissions(['android.permission.CAMERA', 'android.permission.ACCESS_FINE_LOCATION', 'android.permission.CALL_PHONE', 'android.permission.RECORD_AUDIO'], function (e) {
            var denied = (e.deniedAlways || []).concat(e.deniedPresent || [])
            if (denied.length) uni.showModal({ title: '需要权限', content: '请允许相机、定位权限', confirmText: '去设置', success: (r) => { if (r.confirm) plus.runtime.openURL('app-settings://') } })
          })
        } catch (e) { }
      }
    }
  }
}
</script>

<style>
/* ========== Layout ========== */
.page {
  background: var(--bg-page);
  min-height: 100vh;
  padding-bottom: 60px
;width:100%;overflow-x:hidden;box-sizing:border-box;width:100%;overflow-x:hidden;box-sizing:border-box}
.main-content {
  padding: 0 var(--spacing-lg) 60px;
  animation: fadeIn .25s ease
}
.bottom-spacer {
  height: 20px
}

/* ========== Header ========== */
.header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: var(--spacing-lg) 0;
  animation: fadeIn .3s ease
}
.header-top {
  display: flex;
  align-items: center;
  gap: 8px
}
.h-greeting {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.3px;
  line-height: 1.3
}
.h-date {
  font-size: var(--font-sm);
  color: var(--text-tertiary);
  margin-top: 2px;
  display: block
}
.clock-btn {
  border-radius: var(--radius-round);
  background: var(--bg-card);
  border: 1.5px solid var(--border);
  padding: 3px;
  min-height: 34px;
  transition: all .25s;
  flex-shrink: 0
}
.clock-btn:active {
  transform: scale(0.93)
}
.clock-btn.clocked-in {
  border-color: var(--success);
  background: var(--success-bg)
}
.clock-inner {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 0 14px 0 10px
}
.clock-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--text-tertiary);
  transition: all .25s
}
.clock-dot.dot-on {
  background: var(--success);
  box-shadow: 0 0 6px rgba(82, 196, 26, .5)
}
.clock-text {
  font-size: var(--font-sm);
  font-weight: 600;
  color: var(--text-secondary)
}
.clock-btn.clocked-in .clock-text {
  color: var(--success)
}

/* ========== Income Card ========== */
.income-card {
  background: linear-gradient(135deg, #E67A2E, #d4681e);
  border-radius: var(--radius-xl);
  padding: var(--spacing-xl) var(--spacing-xl);
  margin-bottom: var(--spacing-md);
  color: #fff;
  position: relative;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(230, 122, 46, 0.25)
}
.income-card:active {
  opacity: .95
}
.ic-deco {
  position: absolute;
  top: -40px;
  right: -30px;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: rgba(255, 255, 255, .07)
}
.ic-deco::after {
  content: '';
  position: absolute;
  bottom: -30px;
  left: -50px;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: rgba(255, 255, 255, .05)
}
.ic-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-md);
  position: relative
}
.ic-label {
  font-size: var(--font-base);
  opacity: .8
}
.ic-amount {
  font-size: 38px;
  font-weight: 700;
  letter-spacing: -1px;
  line-height: 1.1
}
.ic-badge {
  font-size: var(--font-sm);
  padding: 4px 12px;
  border-radius: var(--radius-round);
  background: rgba(255, 255, 255, .15)
}
.ic-bar {
  display: flex;
  background: rgba(255, 255, 255, .1);
  border-radius: var(--radius-md);
  padding: 12px 8px;
  backdrop-filter: blur(6px)
}
.ic-item {
  flex: 1;
  text-align: center
}
.ic-num {
  font-size: var(--font-xl);
  font-weight: 700;
  display: block
}
.ic-lbl {
  font-size: var(--font-sm);
  opacity: .75;
  margin-top: 2px
}
.ic-vline {
  width: 1px;
  background: rgba(255, 255, 255, .15);
  margin: 4px 0
}

/* ========== Section Headers ========== */
.section-hd {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: var(--spacing-md) 0 var(--spacing-sm)
}
.sh-title {
  font-size: var(--font-lg);
  font-weight: 600;
  color: var(--text-primary)
}
.sh-action {
  font-size: var(--font-sm);
  color: var(--text-tertiary);
  padding: 4px 8px
}

/* ========== 通用卡片网格（竖向） ========== */
.stat-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md)
}
.stat-card {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  padding: var(--spacing-md) var(--spacing-sm);
  text-align: center;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border);
  transition: all .15s
}
.stat-card:active {
  transform: scale(0.95)
}
.sc-num {
  font-size: var(--font-3xl);
  font-weight: 700;
  color: var(--text-primary);
  display: block;
  line-height: 1.2
}
.sc-icon {
  font-size: 22px;
  display: block;
  margin-bottom: 4px
}
.sc-label {
  font-size: var(--font-sm);
  color: var(--text-tertiary);
  margin-top: 4px;
  display: block
}

/* ========== Warn Bar ========== */
.warn-bar {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  background: var(--warning-bg);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md) var(--spacing-lg);
  margin-bottom: var(--spacing-md);
  border-left: 3px solid var(--warning)
}
.warn-icon {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--warning);
  color: #fff;
  text-align: center;
  line-height: 20px;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0
}
.warn-text {
  flex: 1;
  font-size: var(--font-base);
  color: #b45f06;
  line-height: 1.4
}
.warn-action {
  font-size: var(--font-sm);
  color: var(--primary);
  font-weight: 500
}

/* ========== 按日期分组的卡片（竖向排列） ========== */
.date-group {
  margin-bottom: var(--spacing-md)
}
/* 竖向堆叠容器 */
.order-scroll {
  display: block
}
/* 卡片：100% 宽度，竖向依次排列 */
.h-order-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-sm);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 6px
}
.h-order-card:active {
  background: var(--bg-fill)
}
.hoc-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start
}
.hoc-time {
  display: flex;
  align-items: baseline;
  gap: 4px
}
.hoc-time-num {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary);
  line-height: 1.2
}
.hoc-time-unit {
  font-size: var(--font-sm);
  color: var(--text-tertiary)
}
.hoc-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: var(--radius-round);
  background: #f0f2f5;
  color: var(--text-secondary);
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0
}
.hoc-badge.in_progress {
  background: #fff3e0;
  color: var(--primary)
}
.hoc-badge.accepted,
.hoc-badge.booked {
  background: var(--info-bg);
  color: var(--info)
}
.hoc-badge.dispatched {
  background: var(--warning-bg);
  color: #d48806
}
.hoc-badge.CANCEL_PENDING {
  background: #fce4ec;
  color: var(--danger)
}
.hoc-badge.completed,
.hoc-badge.paid,
.hoc-badge.done {
  background: var(--success-bg);
  color: var(--success)
}
.hoc-title {
  font-size: var(--font-md);
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis
}
.hoc-addr {
  font-size: var(--font-sm);
  color: var(--text-tertiary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4
}
.hoc-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  padding-top: 6px;
  border-top: 1px solid var(--border)
}
.hoc-customer {
  font-size: var(--font-sm);
  color: var(--text-secondary);
  font-weight: 500
}
.hoc-fee {
  color: var(--danger);
  font-weight: 700;
  font-size: var(--font-md)
}

/* ========== Empty State ========== */
.empty-section {
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  padding: 50px 20px;
  text-align: center;
  margin: var(--spacing-lg) 0;
  border: 1.5px dashed var(--border-strong)
}
.empty-icon {
  font-size: 40px;
  margin-bottom: var(--spacing-md)
}
.empty-title {
  font-size: var(--font-xl);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-xs)
}
.empty-desc {
  font-size: var(--font-base);
  color: var(--text-tertiary)
}

/* ========== Notifications ========== */
.bell-wrap {
  position: relative;
  padding: 2px
}
.bell-icon {
  font-size: 20px;
  line-height: 1
}
.bell-badge {
  position: absolute;
  top: -6px;
  right: -8px;
  background: var(--danger);
  color: #fff;
  font-size: 9px;
  font-weight: 700;
  min-width: 15px;
  height: 15px;
  line-height: 15px;
  text-align: center;
  border-radius: 7px;
  padding: 0 4px;
  border: 1.5px solid var(--bg-page)
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(6px)
  }
  to {
    opacity: 1;
    transform: translateY(0)
  }
}
</style>
