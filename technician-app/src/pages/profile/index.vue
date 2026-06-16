<template>
  <view class="page">
    <!-- 用户信息头部（点击可编辑） -->
    <view class="profile-header" @click="navTo('/pages/profile/edit')">
      <view class="avatar">{{ user?.name?.charAt(0) || '师' }}</view>
      <view class="profile-name">{{ user?.name || '未登录' }}</view>
      <view class="profile-phone">{{ user?.phone ? user.phone.slice(0,3)+'****'+user.phone.slice(-4) : '' }}</view>
      <view class="profile-status"><view class="pdot"></view><text>在线</text></view>
      <view class="edit-hint">编辑资料 ›</view>
    </view>

    <!-- 统计栏 -->
    <view class="stat-bar">
      <view class="stat-item"><text class="s-num">{{ totalOrders }}</text><text class="s-lbl">累计工单</text></view>
      <view class="stat-item"><text class="s-num">{{ skillCount }}</text><text class="s-lbl">专业技能</text></view>
      <view class="stat-item"><text class="s-num">{{ rating }}</text><text class="s-lbl">评分</text></view>
    </view>

    <!-- 考勤快捷卡片 -->
    <view class="attendance-card" @click="showAttendance">
      <view class="att-header">
        <text class="att-title">📅 本月考勤</text>
        <text class="att-more">详情 ›</text>
      </view>
      <view class="att-stats">
        <view class="att-item"><text class="att-num">{{ attendDays }}</text><text class="att-lbl">出勤(天)</text></view>
        <view class="att-item"><text class="att-num">{{ leaveDays }}</text><text class="att-lbl">请假(天)</text></view>
        <view class="att-item"><text class="att-num" :style="'color:'+(attendRate>80?'var(--success)':'var(--danger)')">{{ attendRate }}%</text><text class="att-lbl">出勤率</text></view>
      </view>
    </view>

    <!-- 菜单组1：工作相关 -->
    <view class="menu-group">
      <view class="menu-item" @click="showDeposit">
        <view class="mi-icon-wrap" style="background:#fff7e6"><text class="mi-icon">🛡️</text></view>
        <text class="mi-label">保证金</text>
        <text class="mi-value" :style="'color:'+(deposit>0?'#52c41a':'#ff4d4f')">¥{{ deposit||0 }}</text>
        <text class="mi-arrow">›</text>
      </view>
      <view class="menu-item" @click="jump('/pages/orders/index')">
        <view class="mi-icon-wrap"><text class="mi-icon">📋</text></view>
        <text class="mi-label">我的工单</text>
        <text class="mi-arrow">›</text>
      </view>
      <view class="menu-item" @click="jump('/pages/income/index')">
        <view class="mi-icon-wrap"><text class="mi-icon">💰</text></view>
        <text class="mi-label">收入中心</text>
        <text class="mi-arrow">›</text>
      </view>
      <view class="menu-item" @click="navTo('/pages/income/withdrawals')">
        <view class="mi-icon-wrap"><text class="mi-icon">💳</text></view>
        <text class="mi-label">提现记录</text>
        <text class="mi-arrow">›</text>
      </view>
    </view>

    <!-- 菜单组2：个人资料 -->
    <view class="menu-group">
      <view class="menu-item" @click="showSkills()">
        <view class="mi-icon-wrap"><text class="mi-icon">🔧</text></view>
        <text class="mi-label">我的技能</text>
        <text class="mi-value">{{ skillCount }}项</text>
        <text class="mi-arrow">›</text>
      </view>
      <view class="menu-item" @click="navTo('/pages/profile/ratings')">
        <view class="mi-icon-wrap"><text class="mi-icon">⭐</text></view>
        <text class="mi-label">我的评价</text>
        <text class="mi-value">{{ rating }}</text>
        <text class="mi-arrow">›</text>
      </view>
      <view class="menu-item" @click="navTo('/pages/profile/edit')">
        <view class="mi-icon-wrap"><text class="mi-icon">📝</text></view>
        <text class="mi-label">个人资料</text>
        <text class="mi-arrow">›</text>
      </view>
    </view>

    <!-- 菜单组3：通知与日程 -->
    <view class="menu-group">
      <view class="menu-item" @click="navTo('/pages/notifications/index')">
        <view class="mi-icon-wrap"><text class="mi-icon">🔔</text></view>
        <text class="mi-label">消息通知</text>
        <text class="mi-value" v-if="unreadCount>0" style="color:var(--danger)">{{ unreadCount }}条未读</text>
        <text class="mi-arrow">›</text>
      </view>
      <view class="menu-item" @click="navTo('/pages/schedule/index')">
        <view class="mi-icon-wrap"><text class="mi-icon">📅</text></view>
        <text class="mi-label">工作日程</text>
        <text class="mi-arrow">›</text>
      </view>
    </view>

    <!-- 菜单组4：账户 -->
    <view class="menu-group">
      <view class="menu-item" @click="changePwd">
        <view class="mi-icon-wrap"><text class="mi-icon">🔑</text></view>
        <text class="mi-label">修改密码</text>
        <text class="mi-arrow">›</text>
      </view>
      <view class="menu-item" @click="navTo('/pages/profile/settings')">
        <view class="mi-icon-wrap"><text class="mi-icon">⚙️</text></view>
        <text class="mi-label">设置</text>
        <text class="mi-arrow">›</text>
      </view>
      <view class="menu-item menu-logout" @click="logout">
        <view class="mi-icon-wrap"><text class="mi-icon">🚪</text></view>
        <text class="mi-label">退出登录</text>
      </view>
    </view>

    <!-- 保证金弹窗 -->
    <view class="modal-overlay" v-if="showDepositDlg" @click="showDepositDlg=false">
      <view class="deposit-box" @click.stop>
        <view class="deposit-header">🛡️ 保证金</view>
        <view class="deposit-balance">
          <text class="deposit-label">当前保证金</text>
          <text class="deposit-amount">¥{{ deposit }}</text>
        </view>
        <view class="deposit-hint">充值保证金后方可接单，平台将从保证金中扣除抽成</view>
        <view class="deposit-presets">
          <text v-for="a in [100,200,500,1000]" :key="a" :class="'deposit-preset '+(depositAmount===a?'active':'')" @click="depositAmount=a">¥{{ a }}</text>
        </view>
        <view class="deposit-custom">
          <text class="deposit-custom-label">自定义金额</text>
          <input class="deposit-input" type="digit" v-model="depositAmount" placeholder="输入金额" />
        </view>
        <button class="deposit-btn" @click="payDeposit">充值 ¥{{ depositAmount }}</button>
        <text class="deposit-close" @click="showDepositDlg=false">取消</text>
      </view>
    </view>

    <!-- 考勤弹窗 -->
    <view class="modal-overlay" v-if="showAttDlg" @click="showAttDlg=false">
      <view class="att-modal" @click.stop>
        <view class="att-modal-header">📅 考勤统计</view>
        <view class="att-modal-body">
          <view class="attm-row"><text class="attm-label">本月出勤</text><text class="attm-val">{{ attendDays }} 天</text></view>
          <view class="attm-row"><text class="attm-label">本月请假</text><text class="attm-val">{{ leaveDays }} 天</text></view>
          <view class="attm-row"><text class="attm-label">出勤率</text><text class="attm-val">{{ attendRate }}%</text></view>
          <view class="attm-row"><text class="attm-label">今日状态</text><text class="attm-val" :style="'color:'+(todayClockIn?'var(--success)':'var(--warning)')">{{ todayClockIn ? '已打卡' : '未打卡' }}</text></view>
        </view>
        <text class="deposit-close" @click="showAttDlg=false">关闭</text>
      </view>
    </view>
  </view>
</template>

<script>
import api from '../../api'
export default {
  data() { return {
    user: null, rating: '暂无', totalOrders: 0, skillCount: 0, skills: [],
    deposit: 0, showDepositDlg: false, depositAmount: 200,
    unreadCount: 0, servicePhone: '4000000000', commissionRate: 80,
    attendDays: 0, leaveDays: 0, attendRate: 100, todayClockIn: false, showAttDlg: false,
    appVersion: '1.0.0',
  }},
  async onShow() {
    this.user = uni.getStorageSync('user')
    if (!this.user) uni.reLaunch({ url: '/pages/login/index' })
    // 串行加载，优先展示缓存数据
    this.loadVersion()
    this.loadCachedData()
    await Promise.all([
      this.loadStats(),
      this.loadDeposit(),
      this.loadUnreadCount(),
      this.loadSettings(),
      this.loadAttendance(),
    ])
    this.cacheData()
  },
  methods: {
    jump(url) { uni.switchTab({ url }) },
    navTo(url) { uni.navigateTo({ url }) },

    // ---- 版本号 ----
    loadVersion() {
      try {
        if (typeof plus !== 'undefined') { this.appVersion = plus.runtime.version || '1.0.0' }
      } catch(e) {}
    },

    // ---- 缓存策略 ----
    loadCachedData() {
      const cached = uni.getStorageSync('profileCache')
      if (cached) {
        this.totalOrders = cached.totalOrders || 0
        this.skillCount = cached.skillCount || 0
        this.rating = cached.rating || '暂无'
        this.attendDays = cached.attendDays || 0
        this.leaveDays = cached.leaveDays || 0
        this.attendRate = cached.attendRate || 100
      }
    },
    cacheData() {
      uni.setStorageSync('profileCache', {
        totalOrders: this.totalOrders,
        skillCount: this.skillCount,
        rating: this.rating,
        attendDays: this.attendDays,
        leaveDays: this.leaveDays,
        attendRate: this.attendRate,
        cachedAt: Date.now(),
      })
    },

    // ---- 工单/技能统计 ----
    async loadStats() {
      try {
        const [res, skillRes] = await Promise.all([
          api.getMyOrders(this.user.id),
          api.getSkills(this.user.id).catch(()=>({data:[]}))
        ])
        const orders = (Array.isArray(res.data) ? res.data : res.data?.items) || []
        this.totalOrders = orders.filter(o => o.status === 'completed' || o.status === 'done' || o.status === 'paid').length
        this.skills = Array.isArray(skillRes.data) ? skillRes.data : (skillRes.data?.skills || [])
        this.skillCount = this.skills.length
        const rated = orders.filter(o => o.rating != null)
        this.rating = rated.length ? (rated.reduce((s,o) => s + o.rating, 0) / rated.length).toFixed(1) : '暂无'
      } catch(e) {}
    },

    // ---- 技能展示（增强版） ----
    showSkills() {
      if (!this.skills || !this.skills.length) {
        uni.showModal({ title: '暂无技能', content: '您还没有添加技能记录，请联系管理员添加', showCancel: false })
        return
      }
      const items = this.skills.map(s => `🔧 ${s.service_name} (${s.level==='senior'?'高级':s.level==='medium'?'中级':'初级'})`)
      items.push('📞 如需修改请联系管理员')
      uni.showActionSheet({ itemList: items, success:()=>{} })
    },

    // ---- 密码修改 ----
    changePwd() {
      if (typeof plus !== 'undefined') {
        plus.nativeUI.prompt('请输入旧密码', (e1) => {
          if (!e1.value) return uni.showToast({title:'请输入旧密码',icon:'none'})
          plus.nativeUI.prompt('请输入新密码（至少6位）', async (e2) => {
            if (!e2.value || e2.value.length < 6) return uni.showToast({title:'密码至少6位',icon:'none'})
            try { await api.changePassword(e1.value, e2.value); plus.nativeUI.alert('密码修改成功') }
            catch(e) { uni.showToast({title:typeof e==='string'?e:(e.message||'修改失败'),icon:'none'}) }
          }, '修改密码', '输入新密码')
        }, '修改密码', '输入旧密码')
      } else {
        var oldPwd = prompt('请输入旧密码:')
        if (!oldPwd) return
        var newPwd = prompt('请输入新密码（至少6位）:')
        if (!newPwd || newPwd.length < 6) { alert('密码至少6位'); return }
        api.changePassword(oldPwd, newPwd).then(()=>{ alert('密码修改成功') }).catch((e)=>{ alert('修改失败') })
      }
    },

    // ---- 保证金 ----
    showDeposit() { this.showDepositDlg = true },
    async loadDeposit() {
      try { const res = await api.getDeposit(this.user.id); if (res.data) this.deposit = res.data.deposit || 0 } catch(e) {}
    },
    async payDeposit() {
      if (this.depositAmount < 100) { uni.showToast({ title:'最低充值¥100', icon:'none' }); return }
      try { await api.payDeposit(this.user.id, { amount: this.depositAmount }); this.showDepositDlg = false; uni.showToast({ title:'申请已提交，等待管理员审核', icon:'none' }) } catch(e) { uni.showToast({ title: e.message, icon:'none' }) }
    },

    // ---- 通知 ----
    async loadUnreadCount() {
      try { const res = await api.getUnreadCount(); this.unreadCount = res.data?.count || 0 } catch(e) {}
    },

    // ---- 设置 ----
    async loadSettings() {
      try {
        const res = await api.getPublicSettings()
        const d = res.data || {}
        this.servicePhone = d.customer_service_phone || '4000000000'
        this.commissionRate = d.commission_rate || 80
        uni.setStorageSync('servicePhone', this.servicePhone)
      } catch(e) {}
    },

    // ---- 考勤统计 ----
    async loadAttendance() {
      try {
        const [attRes, leaveRes] = await Promise.all([
          api.getAttendanceToday(this.user.id).catch(()=>({data:{}})),
          api.getMyLeaves(this.user.id).catch(()=>({data:[]})),
        ])
        // 今日打卡状态（API返回 {data: {attendances: [...]}}）
        const attData = attRes.data || {}
        const atts = attData.attendances || []
        this.todayClockIn = atts.length > 0 && atts[0].clock_in ? true : false
        // 当月请假天数
        const leaves = Array.isArray(leaveRes.data) ? leaveRes.data : []
        const now = new Date()
        const ym = now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0')
        const monthLeaves = leaves.filter(l =>
          (l.status === 'approved') &&
          (l.created_at||'').startsWith(ym)
        )
        this.leaveDays = monthLeaves.reduce((s, l) => s + (l.days || 1), 0)

        // 估算出勤天数（从本月1号到今天，去掉周末和请假天数）
        const monthStart = new Date(now.getFullYear(), now.getMonth(), 1)
        const totalDays = Math.floor((now - monthStart) / 86400000) + 1
        // 简单估算：工作日出勤 ≈ 总天数 - 周末数 - 请假
        let weekends = 0
        for (let d = new Date(monthStart); d <= now; d.setDate(d.getDate() + 1)) {
          if (d.getDay() === 0 || d.getDay() === 6) weekends++
        }
        // 假定师傅工作日都正常打卡
        const workDays = totalDays - weekends
        this.attendDays = Math.max(0, workDays - this.leaveDays)
        this.attendRate = workDays > 0 ? Math.round(this.attendDays / workDays * 100) : 100
      } catch(e) {}
    },

    // ---- 考勤弹窗 ----
    showAttendance() { this.showAttDlg = true },

    // ---- 退出登录 ----
    logout() {
      uni.showModal({ title:'提示', content:'确定退出登录？', success:(r)=>{
        if(r.confirm){
          uni.removeStorageSync('token')
          uni.removeStorageSync('user')
          uni.removeStorageSync('profileCache')
          uni.reLaunch({ url:'/pages/login/index' })
        }
      }})
    }
  }
}
</script>

<style>
.page{background:var(--bg-page);min-height:100vh;padding:var(--spacing-md);padding-bottom:60px;width:100%;overflow-x:hidden;box-sizing:border-box}

/* 头部 */
.profile-header{background:var(--primary-gradient);border-radius:var(--radius-lg);padding:32px 20px 22px;text-align:center;color:#fff;margin-bottom:var(--spacing-md);position:relative;overflow:hidden}
.profile-header::after{content:'';position:absolute;top:-30px;right:-30px;width:100px;height:100px;border-radius:50%;background:rgba(255,255,255,.05)}
.profile-header:active{opacity:.92}
.avatar{width:68px;height:68px;border-radius:50%;background:rgba(255,255,255,.2);display:flex;align-items:center;justify-content:center;font-size:30px;font-weight:600;margin:0 auto var(--spacing-sm);border:3px solid rgba(255,255,255,.3)}
.profile-name{font-size:var(--font-2xl);font-weight:700}
.profile-phone{font-size:var(--font-base);opacity:.7;margin-top:4px}
.profile-status{display:flex;align-items:center;justify-content:center;gap:6px;margin-top:8px;font-size:var(--font-sm);opacity:.8}
.pdot{width:8px;height:8px;border-radius:50%;background:var(--success);box-shadow:0 0 6px rgba(82,196,26,.5)}
.edit-hint{position:absolute;right:16px;bottom:12px;font-size:var(--font-sm);opacity:.6}

/* 统计栏 */
.stat-bar{display:flex;background:var(--bg-card);border-radius:var(--radius-md);padding:var(--spacing-lg);margin-bottom:var(--spacing-md);box-shadow:var(--shadow-sm);border:1px solid var(--border)}
.stat-item{flex:1;text-align:center}
.s-num{font-size:var(--font-2xl);font-weight:700;display:block;color:var(--primary)}
.s-lbl{font-size:var(--font-sm);color:var(--text-tertiary);margin-top:2px;display:block}

/* 考勤卡片 */
.attendance-card{background:var(--bg-card);border-radius:var(--radius-md);padding:var(--spacing-lg);margin-bottom:var(--spacing-md);box-shadow:var(--shadow-sm);border:1px solid var(--border)}
.attendance-card:active{background:var(--bg-fill)}
.att-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:var(--spacing-sm)}
.att-title{font-weight:600;font-size:var(--font-md);color:var(--text-primary)}
.att-more{font-size:var(--font-sm);color:var(--primary)}
.att-stats{display:flex;gap:var(--spacing-sm)}
.att-item{flex:1;text-align:center;background:var(--bg-fill);border-radius:var(--radius-sm);padding:var(--spacing-sm)}
.att-num{font-size:var(--font-lg);font-weight:700;color:var(--text-primary);display:block}
.att-lbl{font-size:var(--font-sm);color:var(--text-tertiary);margin-top:2px;display:block}

/* 菜单组 */
.menu-group{background:var(--bg-card);border-radius:var(--radius-md);margin-bottom:var(--spacing-md);overflow:hidden;box-shadow:var(--shadow-sm);border:1px solid var(--border)}
.menu-item{display:flex;align-items:center;padding:var(--spacing-lg);border-bottom:1px solid var(--border);font-size:var(--font-md);transition:background .15s}
.menu-item:active{background:var(--bg-fill)}
.menu-item:last-child{border-bottom:none}
.mi-icon-wrap{width:32px;height:32px;border-radius:var(--radius-sm);background:var(--bg-fill);display:flex;align-items:center;justify-content:center;margin-right:var(--spacing-sm);flex-shrink:0}
.mi-icon{font-size:var(--font-lg)}
.mi-label{flex:1;color:var(--text-primary);font-weight:500}
.mi-value{color:var(--primary);font-weight:500;margin-right:var(--spacing-sm);font-size:var(--font-sm)}
.mi-arrow{color:var(--text-tertiary);font-size:var(--font-xl)}
.menu-logout .mi-label{color:var(--danger)}

/* 保证金弹窗 */
.deposit-box{background:#fff;border-radius:20px;padding:28px 24px;width:88%;max-width:360px;text-align:center}
.deposit-header{font-size:22px;font-weight:700;margin-bottom:16px}
.deposit-balance{background:linear-gradient(135deg,#667eea,#764ba2);border-radius:14px;padding:16px;color:#fff;margin-bottom:14px}
.deposit-label{font-size:13px;opacity:.8;display:block}
.deposit-amount{font-size:36px;font-weight:700;display:block;margin-top:4px}
.deposit-hint{font-size:13px;color:#999;margin-bottom:14px;line-height:1.5}
.deposit-presets{display:flex;gap:8px;margin-bottom:12px}
.deposit-preset{flex:1;padding:10px;border:1.5px solid #e0e0e0;border-radius:10px;font-size:15px;font-weight:600;color:#666;text-align:center}
.deposit-preset.active{border-color:#E67A2E;color:#E67A2E;background:#fff5eb}
.deposit-custom{display:flex;align-items:center;gap:8px;margin-bottom:16px;padding:8px 12px;background:#f8f9fb;border-radius:10px}
.deposit-custom-label{font-size:13px;color:#999;white-space:nowrap}
.deposit-input{flex:1;border:none;background:none;font-size:16px;text-align:right;padding:4px 0;outline:none}
.deposit-btn{width:100%;padding:14px;border:none;border-radius:12px;background:linear-gradient(135deg,#E67A2E,#C96A1F);color:#fff;font-size:17px;font-weight:600}
.deposit-close{display:block;text-align:center;font-size:14px;color:#999;margin-top:12px}

/* 考勤弹窗 */
.att-modal{background:#fff;border-radius:20px;padding:28px 24px;width:80%;max-width:340px}
.att-modal-header{font-size:20px;font-weight:700;text-align:center;margin-bottom:var(--spacing-lg)}
.att-modal-body{display:flex;flex-direction:column;gap:var(--spacing-sm);margin-bottom:var(--spacing-md)}
.attm-row{display:flex;justify-content:space-between;padding:var(--spacing-sm) 0;border-bottom:1px solid var(--border)}
.attm-label{font-size:var(--font-md);color:var(--text-secondary)}
.attm-val{font-size:var(--font-md);font-weight:600;color:var(--text-primary)}

.modal-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.4);z-index:100;display:flex;align-items:center;justify-content:center;padding:20px}
</style>
