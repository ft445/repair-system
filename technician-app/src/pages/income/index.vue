<template>
  <div class="page">
    <div class="header-card">
      <div class="header-top">
        <span class="header-label">累计收入</span>
        <span class="header-amount">¥{{ totalEarned }}</span>
      </div>
      <div class="header-stats">
        <div class="hs-item"><span class="hs-num">¥{{ thisMonthEarn }}</span><span class="hs-lbl">本月收入</span></div>
        <div class="hs-item"><span class="hs-num">{{ thisMonthCount }}</span><span class="hs-lbl">本月完成</span></div>
        <div class="hs-item"><span class="hs-num">¥{{ balance }}</span><span class="hs-lbl">可提现</span></div>
      </div>
      <!-- 排名 -->
      <div class="rank-badge" v-if="rank && totalTechs">
        <span class="rank-text">🏆 本月排名 {{ rank }}/{{ totalTechs }}</span>
      </div>
    </div>

    <div class="action-row">
      <div class="action-btn" @click="showWithdraw = true">
        <span class="action-icon">💳</span>
        <span class="action-text">申请提现</span>
      </div>
      <div class="action-btn" @click="loadData()">
        <span class="action-icon">🔄</span>
        <span class="action-text">刷新</span>
      </div>
    </div>

    <div class="section-title">本月收入明细</div>
    <div v-if="dailyEarns.length === 0" class="empty-state">
      <div class="empty-circle">💰</div>
      <span class="empty-text">暂无收入记录</span>
      <span class="empty-desc">完成工单后将显示在这里</span>
    </div>
    <div v-for="(day, i) in dailyEarns" :key="i" class="day-card">
      <div class="day-header">
        <span class="day-date">{{ day.date }}</span>
        <span class="day-total">+¥{{ day.total }}</span>
      </div>
      <div v-for="item in day.items" :key="item.id" class="income-item">
        <div class="ii-left">
          <span class="ii-service">{{ item.service_item_name || '维修' }}</span>
          <span class="ii-addr">{{ item.address?.slice(0,20) || '' }}</span>
        </div>
        <div class="ii-right">
          <span :class="'ii-status '+(item.pay_status==='paid'?'paid':'unpaid')">{{ item.pay_status==='paid'?'已付':'未付' }}</span>
          <span class="ii-amount">+¥{{ item.total_fee || 0 }}</span>
        </div>
      </div>
    </div>

    <!-- 提现弹窗 -->
    <div class="modal-overlay" v-if="showWithdraw" @click="showWithdraw=false">
      <div class="modal-box" @click.stop>
        <div class="modal-title">申请提现</div>
        <div class="modal-balance">可提现余额：¥{{ balance }}</div>
        <div class="form-row">
          <span class="form-label">金额</span>
          <input class="form-input" type="digit" v-model="withdrawAmount" placeholder="输入提现金额" />
        </div>
        <div class="form-row">
          <span class="form-label">方式</span>
          <select :value="withdrawMethod" @change="e=>withdrawMethod=e.target.value" style="flex:1;padding:10px 12px;border:1.5px solid var(--border,#e8e8e8);border-radius:10px;font-size:15px;background:var(--bg-fill,#f8f9fb);color:var(--text-primary)">
            <option v-for="m in withdrawMethods" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>
        <div class="modal-actions">
          <button class="mbtn cancel" @click="showWithdraw=false">取消</button>
          <button class="mbtn confirm" @click="doWithdraw">确认提现</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../api'
export default {
  data() { return { totalEarned: 0, balance: 0, thisMonthEarn: 0, thisMonthCount: 0, dailyEarns: [], user: null, showWithdraw: false, withdrawAmount: '', withdrawMethod: '微信', withdrawMethods: ['微信', '支付宝', '银行卡'], rank: 0, totalTechs: 0, avgRating: null, _reqId: 0 } },
  onShow() { this.user = uni.getStorageSync('user'); if (!this.user) return uni.reLaunch({ url: '/pages/login/index' }); this.loadData() },
  methods: {
    async loadData() {
      const reqId = ++this._reqId
      this.dailyEarns = []; this.totalEarned = 0; this.balance = 0
      try {
        const [orderRes, statsRes] = await Promise.all([
          api.getMyOrders(this.user.id),
          api.getMonthlyStats(this.user.id).catch(() => ({ data: {} })),
        ])
        if (reqId !== this._reqId) return
        const orders = (Array.isArray(orderRes.data) ? orderRes.data : orderRes.data?.items) || []
        const stats = statsRes.data || {}
        this.rank = stats.rank || 0
        this.totalTechs = stats.total_techs || 0
        this.avgRating = stats.avg_rating || null

        const done = orders.filter(o => (o.status === 'completed' || o.status === 'done' || o.status === 'paid') && o.total_fee && Number(o.total_fee) > 0)
        this.totalEarned = done.reduce((s, o) => s + (o.total_fee || 0), 0)
        this.balance = Math.floor(this.totalEarned * 0.8)
        const now = new Date(), ym = now.getFullYear()+'-'+String(now.getMonth()+1).padStart(2,'0')
        const month = done.filter(o => (o.completed_at||o.paid_at||o.created_at||'').startsWith(ym))
        this.thisMonthEarn = month.reduce((s, o) => s + (o.total_fee || 0), 0); this.thisMonthCount = month.length
        const daily = {}
        month.forEach(o => { const d = (o.completed_at||o.paid_at||o.created_at||'').slice(0,10)||'未知日期'; if(!daily[d])daily[d]={date:d,total:0,items:[]}; daily[d].total+=o.total_fee||0; daily[d].items.push(o) })
        this.dailyEarns = Object.values(daily).sort((a,b) => b.date.localeCompare(a.date))
      } catch(e) { console.error(e) }
    },
    async doWithdraw() {
      const amt = Number(this.withdrawAmount)
      if (!amt || amt <= 0) { uni.showToast({ title: '请输入有效金额', icon: 'none' }); return }
      if (amt > this.balance) { uni.showToast({ title: '余额不足', icon: 'none' }); return }
      const mgr = {'微信':'wechat','支付宝':'alipay','银行卡':'bank'}
      try { await api.createWithdraw({ amount: amt, method: mgr[this.withdrawMethod]||'wechat', user_id: this.user.id }); uni.showToast({ title: '提现申请已提交' }); this.showWithdraw = false; this.loadData() }
      catch(e) { uni.showToast({ title: e.message || '提现失败', icon:'none' }) }
    }
  }
}
</script>

<style>
.page{background:var(--bg-page);min-height:100vh;padding:var(--spacing-md);padding-bottom:60px;width:100%;overflow-x:hidden;box-sizing:border-box}
.header-card{background:var(--primary-gradient);border-radius:var(--radius-lg);padding:28px 20px;color:#fff;margin-bottom:var(--spacing-md);box-shadow:0 4px 16px rgba(230,122,46,.3)}
.header-top{text-align:center;margin-bottom:var(--spacing-lg)}
.header-label{font-size:var(--font-sm);opacity:.7}
.header-amount{font-size:40px;font-weight:700;display:block;margin:4px 0}
.header-stats{display:flex;gap:var(--spacing-sm)}
.hs-item{flex:1;text-align:center;background:rgba(255,255,255,.12);border-radius:var(--radius-sm);padding:12px}
.hs-num{font-size:var(--font-lg);font-weight:700;display:block}
.hs-lbl{font-size:var(--font-sm);opacity:.7;margin-top:2px;display:block}
.rank-badge{text-align:center;margin-top:var(--spacing-sm);padding:4px 12px;background:rgba(255,255,255,.15);border-radius:var(--radius-round);display:inline-block;align-self:center}
.rank-text{font-size:var(--font-sm);color:#fff;opacity:.9}
.action-row{display:flex;gap:var(--spacing-sm);margin-bottom:var(--spacing-lg)}
.action-btn{flex:1;background:var(--bg-card);border-radius:var(--radius-md);padding:var(--spacing-lg);text-align:center;font-size:var(--font-sm);box-shadow:var(--shadow-sm);border:1px solid var(--border);transition:all .15s}
.action-btn:active{transform:scale(.97)}
.action-icon{font-size:24px;display:block;margin-bottom:6px}
.action-text{color:var(--text-secondary);font-weight:500}
.section-title{font-size:var(--font-lg);font-weight:600;margin-bottom:var(--spacing-md);color:var(--text-primary)}
.day-card{background:var(--bg-card);border-radius:var(--radius-md);padding:var(--spacing-lg);margin-bottom:var(--spacing-sm);box-shadow:var(--shadow-sm);border:1px solid var(--border)}
.day-header{display:flex;justify-content:space-between;padding-bottom:var(--spacing-sm);border-bottom:1px solid var(--border);margin-bottom:var(--spacing-sm)}
.day-date{font-weight:600;font-size:var(--font-md);color:var(--text-primary)}
.day-total{color:var(--success);font-weight:700;font-size:var(--font-md)}
.income-item{display:flex;justify-content:space-between;align-items:center;padding:var(--spacing-sm) 0;border-bottom:1px solid var(--border)}
.income-item:last-child{border-bottom:none}
.ii-left{flex:1}
.ii-service{font-size:var(--font-base);color:var(--text-primary);display:block}
.ii-addr{font-size:var(--font-sm);color:var(--text-tertiary);margin-top:2px;display:block}
.ii-right{text-align:right}
.ii-status{font-size:var(--font-sm);padding:2px 8px;border-radius:var(--radius-sm);font-weight:500}
.ii-status.paid{background:var(--success-bg);color:var(--success)}
.ii-status.unpaid{background:var(--warning-bg);color:#d48806}
.ii-amount{color:var(--success);font-weight:600;font-size:var(--font-md);display:block;margin-top:2px}
.empty-state{text-align:center;padding:60px 0;background:var(--bg-card);border-radius:var(--radius-md);border:1px dashed var(--border-strong)}
.empty-circle{width:56px;height:56px;border-radius:50%;background:var(--bg-fill);display:flex;align-items:center;justify-content:center;margin:0 auto var(--spacing-md);font-size:24px}
.empty-text{color:var(--text-tertiary);font-size:var(--font-lg);margin-bottom:4px;font-weight:500}
.empty-desc{color:var(--text-tertiary);font-size:var(--font-sm)}
/* Modal */
.modal-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.4);z-index:100;display:flex;align-items:center;justify-content:center;padding:20px;backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px)}
@supports not (backdrop-filter:blur(4px)){.modal-overlay{backdrop-filter:none}}
.modal-box{background:var(--bg-card);border-radius:var(--radius-lg);padding:var(--spacing-xl);width:85%;max-width:360px}
.modal-title{font-size:var(--font-xl);font-weight:700;margin-bottom:var(--spacing-sm);text-align:center;color:var(--text-primary)}
.modal-balance{font-size:var(--font-sm);color:var(--text-tertiary);margin-bottom:var(--spacing-lg);text-align:center}
.form-row{display:flex;align-items:center;gap:var(--spacing-sm);margin-bottom:var(--spacing-md)}
.form-label{font-size:var(--font-base);color:var(--text-secondary);width:50px;flex-shrink:0;font-weight:500}
.form-input{flex:1;padding:var(--spacing-sm) var(--spacing-md);border:1.5px solid var(--border);border-radius:var(--radius-sm);font-size:var(--font-md);background:var(--bg-fill)}
.form-picker{display:flex;align-items:center;min-height:40px}
.modal-actions{display:flex;gap:var(--spacing-sm);margin-top:var(--spacing-xl)}
.mbtn{flex:1;padding:12px;border:none;border-radius:var(--radius-sm);font-size:var(--font-md);font-weight:600}
.mbtn.cancel{background:var(--bg-fill);color:var(--text-secondary)}
.mbtn.confirm{background:var(--primary-gradient);color:#fff}
</style>
