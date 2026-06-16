<template>
  <view class="page">
    <!-- 月份切换 -->
    <view class="month-bar">
      <text class="month-nav" @click="prevMonth">‹</text>
      <text class="month-title">{{ year }}年{{ month }}月</text>
      <text class="month-nav" @click="nextMonth">›</text>
    </view>

    <!-- 星期头 -->
    <view class="week-header">
      <text v-for="w in weekdays" :key="w" class="week-day">{{ w }}</text>
    </view>

    <!-- 日历网格 -->
    <view class="calendar-grid">
      <view v-for="(d, i) in calendarDays" :key="i"
        :class="'cal-cell '+(d.isToday?'today':'')+' '+(d.isCurrentMonth?'':'other-month')+' '+(d.isSelected?'selected':'')"
        @click="selectDay(d)"
      >
        <text class="cal-date">{{ d.day }}</text>
        <view class="cal-dot" v-if="d.hasOrder"></view>
      </view>
    </view>

    <!-- 繁忙统计 -->
    <view class="stats-bar">
      <view class="stats-item"><text class="stats-num">{{ todayOrders.length }}</text><text class="stats-lbl">今日工单</text></view>
      <view class="stats-item"><text class="stats-num">{{ tomorrowOrders.length }}</text><text class="stats-lbl">明日工单</text></view>
      <view class="stats-item"><text class="stats-num">{{ monthOrderCount }}</text><text class="stats-lbl">本月工单</text></view>
    </view>

    <!-- 选中日期工单 -->
    <view class="section-title" v-if="selectedOrders.length">
      <text>{{ selectedDateLabel }} 工单（{{ selectedOrders.length }}）</text>
    </view>
    <view v-if="selectedOrders.length === 0 && !loading" class="empty-section">
      <text class="empty-hint">{{ selectedDateLabel }} 暂无安排</text>
    </view>
    <view v-for="item in selectedOrders" :key="item.id" class="task-card" @click="goDetail(item.id)">
      <view class="task-header">
        <text class="task-time">{{ item.time || '待定' }}</text>
        <text :class="'task-status ' + item.status">{{ statusTxt(item.status) }}</text>
      </view>
      <view class="task-title">{{ item.service_item_name || '维修' }}</view>
      <view class="task-addr">{{ item.customer_name || '客户' }} · {{ (item.address||'').slice(0,25) }}</view>
    </view>

    <!-- 今日快捷 -->
    <view class="quick-bar">
      <text class="quick-btn" @click="jumpToday">📅 今日安排</text>
      <text class="quick-btn" @click="jumpTomorrow">📆 明日安排</text>
      <text class="quick-btn" @click="jumpAll">📋 本月全部</text>
    </view>

    <view style="height:30px"></view>
  </view>
</template>

<script>
import api from '../../api'
export default {
  data() {
    return {
      user: null, loading: true,
      year: 0, month: 0,
      weekdays: ['日','一','二','三','四','五','六'],
      calendarDays: [],
      orders: [],
      todayOrders: [],
      tomorrowOrders: [],
      monthOrderCount: 0,
      selectedDate: '',
      selectedOrders: [],
    }
  },
  computed: {
    selectedDateLabel() {
      if (!this.selectedDate) return ''
      const parts = this.selectedDate.split('-')
      return parseInt(parts[1]) + '月' + parseInt(parts[2]) + '日'
    }
  },
  onLoad() {
    this.user = uni.getStorageSync('user')
    if (!this.user) return uni.reLaunch({ url: '/pages/login/index' })
    const now = new Date()
    this.year = now.getFullYear()
    this.month = now.getMonth() + 1
    this.selectedDate = now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0')+'-'+String(now.getDate()).padStart(2,'0')
    this.buildCalendar()
    this.loadOrders()
  },
  onPullDownRefresh() {
    this.loadOrders().then(() => uni.stopPullDownRefresh())
  },
  methods: {
    statusTxt(s) { const m={pending:'待接单',dispatched:'已派单',accepted:'已接单',in_progress:'进行中',completed:'已完成',paid:'已付款',done:'已完成',cancelled:'已取消',CANCEL_PENDING:'待审核'}; return m[s]||s },
    goDetail(id) { uni.navigateTo({ url:'/pages/orders/detail?id='+id }) },
    prevMonth() {
      if (this.month === 1) { this.year--; this.month = 12 }
      else { this.month-- }
      this.buildCalendar()
      this.loadOrders()
    },
    nextMonth() {
      if (this.month === 12) { this.year++; this.month = 1 }
      else { this.month++ }
      this.buildCalendar()
      this.loadOrders()
    },
    jumpToday() {
      const n=new Date()
      this.selectedDate = n.getFullYear()+'-'+String(n.getMonth()+1).padStart(2,'0')+'-'+String(n.getDate()).padStart(2,'0')
      this.updateSelectedOrders()
    },
    jumpTomorrow() {
      const n=new Date(Date.now()+864e5)
      this.selectedDate = n.getFullYear()+'-'+String(n.getMonth()+1).padStart(2,'0')+'-'+String(n.getDate()).padStart(2,'0')
      this.updateSelectedOrders()
    },
    jumpAll() {
      this.selectedOrders = this.orders
    },
    buildCalendar() {
      const firstDay = new Date(this.year, this.month - 1, 1)
      const lastDay = new Date(this.year, this.month, 0)
      const startWeekday = firstDay.getDay()
      const daysInMonth = lastDay.getDate()
      const prevMonthDays = new Date(this.year, this.month - 1, 0).getDate()
      const n=new Date(); const todayStr = n.getFullYear()+'-'+String(n.getMonth()+1).padStart(2,'0')+'-'+String(n.getDate()).padStart(2,'0')

      const days = []
      // 上月填充
      for (let i = startWeekday - 1; i >= 0; i--) {
        const d = prevMonthDays - i
        const m = this.month === 1 ? 12 : this.month - 1
        const y = this.month === 1 ? this.year - 1 : this.year
        days.push({ day: d, fullDate: `${y}-${String(m).padStart(2,'0')}-${String(d).padStart(2,'0')}`, isCurrentMonth: false, isToday: false, hasOrder: false, isSelected: false })
      }
      // 当月
      for (let i = 1; i <= daysInMonth; i++) {
        const fullDate = `${this.year}-${String(this.month).padStart(2,'0')}-${String(i).padStart(2,'0')}`
        days.push({ day: i, fullDate, isCurrentMonth: true, isToday: fullDate === todayStr, hasOrder: false, isSelected: fullDate === this.selectedDate })
      }
      // 下月填充（补满6行=42格）
      const remaining = 42 - days.length
      for (let i = 1; i <= remaining; i++) {
        const m = this.month === 12 ? 1 : this.month + 1
        const y = this.month === 12 ? this.year + 1 : this.year
        days.push({ day: i, fullDate: `${y}-${String(m).padStart(2,'0')}-${String(i).padStart(2,'0')}`, isCurrentMonth: false, isToday: false, hasOrder: false, isSelected: false })
      }
      this.calendarDays = days
    },
    async loadOrders() {
      this.loading = true
      try {
        // 计算当月最后一天（解决28/29/30/31不同月份的问题）
        const lastDay = new Date(this.year, this.month, 0).getDate()
        const startDate = `${this.year}-${String(this.month).padStart(2,'0')}-01`
        const endDate = `${this.year}-${String(this.month).padStart(2,'0')}-${String(lastDay).padStart(2,'0')}`
        const res = await api.getSchedule(this.user.id, startDate, endDate)
        this.orders = res.data?.items || []

        // 为每个工单提取日期（优先取 appointment_time 再取 created_at）
        this.orders.forEach(o => { o._day = (o.appointment_time||o.created_at||'').slice(0,10) })

        // 标记日历中有工单的日期
        const orderDays = new Set()
        this.orders.forEach(o => { if (o._day) orderDays.add(o._day) })
        this.calendarDays.forEach(d => { d.hasOrder = orderDays.has(d.fullDate) })

        // 统计数据
        const n=new Date()
        const today = n.getFullYear()+'-'+String(n.getMonth()+1).padStart(2,'0')+'-'+String(n.getDate()).padStart(2,'0')
        const tn=new Date(Date.now()+864e5)
        const tomorrow = tn.getFullYear()+'-'+String(tn.getMonth()+1).padStart(2,'0')+'-'+String(tn.getDate()).padStart(2,'0')
        this.todayOrders = this.orders.filter(o => o._day === today)
        this.tomorrowOrders = this.orders.filter(o => o._day === tomorrow)
        this.monthOrderCount = this.orders.length

        this.updateSelectedOrders()
      } catch(e) { console.error(e) }
      finally { this.loading = false }
    },
    selectDay(d) {
      this.selectedDate = d.fullDate
      this.calendarDays.forEach(cd => { cd.isSelected = cd.fullDate === d.fullDate })
      this.updateSelectedOrders()
    },
    updateSelectedOrders() {
      this.selectedOrders = this.orders.filter(o => o._day === this.selectedDate)
    }
  }
}
</script>

<style>
.page{background:var(--bg-page);min-height:100vh;width:100%;overflow-x:hidden;box-sizing:border-box}

.month-bar{display:flex;align-items:center;justify-content:space-between;background:var(--bg-card);padding:var(--spacing-md) var(--spacing-lg);border-bottom:1px solid var(--border)}
.month-nav{font-size:28px;color:var(--primary);font-weight:300;padding:0 var(--spacing-sm);line-height:1}
.month-title{font-size:var(--font-xl);font-weight:700;color:var(--text-primary)}

.week-header{display:grid;grid-template-columns:repeat(7,1fr);background:var(--bg-fill);padding:var(--spacing-sm) 0}
.week-day{text-align:center;font-size:var(--font-sm);color:var(--text-tertiary);font-weight:500}

.calendar-grid{display:grid;grid-template-columns:repeat(7,1fr);background:var(--bg-card);padding:var(--spacing-xs) 0}
.cal-cell{text-align:center;padding:var(--spacing-sm) 0;position:relative;display:flex;flex-direction:column;align-items:center;min-height:44px;justify-content:center}
.cal-cell.other-month .cal-date{color:var(--text-tertiary);opacity:.4}
.cal-cell.today .cal-date{background:var(--primary-gradient);color:#fff;border-radius:50%;width:30px;height:30px;line-height:30px;font-weight:700}
.cal-cell.selected .cal-date{background:var(--primary-light);color:var(--primary);border-radius:50%;width:30px;height:30px;line-height:30px;font-weight:700}
.cal-date{font-size:var(--font-md);color:var(--text-primary);font-weight:500;transition:all .15s}
.cal-dot{width:5px;height:5px;border-radius:50%;background:var(--primary);margin-top:2px}

.stats-bar{display:flex;background:var(--bg-card);margin:var(--spacing-sm) var(--spacing-md);border-radius:var(--radius-md);padding:var(--spacing-lg);box-shadow:var(--shadow-sm);border:1px solid var(--border)}
.stats-item{flex:1;text-align:center}
.stats-num{font-size:var(--font-2xl);font-weight:700;color:var(--primary);display:block}
.stats-lbl{font-size:var(--font-sm);color:var(--text-tertiary);margin-top:2px}

.section-title{font-size:var(--font-lg);font-weight:600;margin:var(--spacing-md) var(--spacing-md) var(--spacing-sm);color:var(--text-primary)}
.empty-section{text-align:center;padding:var(--spacing-xl) 0}
.empty-hint{font-size:var(--font-base);color:var(--text-tertiary)}

.task-card{background:var(--bg-card);border-radius:var(--radius-lg);padding:var(--spacing-lg);margin:0 var(--spacing-md) var(--spacing-sm);box-shadow:var(--shadow-sm);border:1px solid var(--border);transition:all .2s}
.task-card:active{transform:scale(0.98)}
.task-header{display:flex;justify-content:space-between;margin-bottom:6px}
.task-time{font-size:var(--font-sm);color:var(--text-tertiary);font-weight:500}
.task-status{font-size:var(--font-sm);padding:2px 10px;border-radius:var(--radius-sm);font-weight:500;background:#f0f2f5;color:var(--text-secondary)}
.task-status.in_progress{background:#fff3e0;color:var(--primary)}
.task-status.accepted{background:var(--info-bg);color:var(--info)}
.task-title{font-size:var(--font-md);font-weight:600;color:var(--text-primary);margin-bottom:4px}
.task-addr{font-size:var(--font-sm);color:var(--text-secondary);background:var(--bg-fill);padding:6px 8px;border-radius:var(--radius-sm)}

.quick-bar{display:flex;gap:var(--spacing-sm);margin:var(--spacing-lg) var(--spacing-md) 0}
.quick-btn{flex:1;text-align:center;padding:var(--spacing-sm);background:var(--bg-card);border-radius:var(--radius-sm);font-size:var(--font-sm);color:var(--text-secondary);border:1px solid var(--border)}
</style>
