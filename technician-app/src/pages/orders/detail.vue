<template>
  <view class="page">
    <!-- Skeleton -->
    <view v-if="loading" class="skeleton-wrap">
      <view class="skeleton-card" style="height:70px;display:flex;gap:12px;padding:16px;align-items:center">
        <view class="skeleton-block" style="width:40px;height:40px;border-radius:50%;flex-shrink:0"></view>
        <view style="flex:1"><view class="skeleton-line w60"></view><view class="skeleton-line w40"></view></view>
      </view>
      <view class="skeleton-card" style="height:120px"><view class="skeleton-line w40"></view><view class="skeleton-line w80"></view><view class="skeleton-line w60"></view></view>
      <view class="skeleton-card" style="height:80px"><view class="skeleton-line w40"></view><view class="skeleton-line w80 h32"></view></view>
    </view>

    <view v-else-if="order" class="detail-wrap">
      <!-- Status Header -->
      <view class="status-header" :class="order.status">
        <view class="status-left">
          <view class="status-icon-circle">{{ statusIcon(order.status) }}</view>
          <view>
            <text class="status-title">{{ statusLabel(order.status) }}</text>
            <text class="order-no">单号: {{ order.order_no }}</text>
            <text class="copy-btn" @click="copyText(order.order_no,'工单号')">复制单号</text>
          </view>
        </view>
        <text class="status-time">{{ order.created_at ? parseInt(order.created_at.slice(5,7))+'月'+parseInt(order.created_at.slice(8,10))+'日 '+order.created_at.slice(11,16) : '' }}</text>
      </view>

      <!-- Order Timeline -->
      <view class="timeline-wrap" v-if="showTimeline">
        <view class="tl-step" v-for="(s,i) in timelineSteps" :key="i" :class="s.done?'tl-done':'tl-pending'">
          <view class="tl-dot"></view>
          <text class="tl-label">{{ s.label }}</text>
          <view class="tl-line" v-if="i < timelineSteps.length-1" :class="s.done?'tl-line-done':''"></view>
        </view>
      </view>

      <!-- Customer Info -->
      <view class="customer-card">
        <view class="cc-top">
          <view class="cc-avatar">{{ (order.customer_name||'客').charAt(0) }}</view>
          <view class="cc-info">
            <text class="cc-name">{{ order.customer_name||'客户' }}</text>
            <text class="cc-phone">{{ order.customer_phone ? order.customer_phone.slice(0,3)+'****'+order.customer_phone.slice(-4) : '' }}</text>
          </view>
          <view class="cc-actions">
            <view class="cc-icon" @click="callCustomer">📞</view>
            <view class="cc-icon" @click="smsCustomer">💬</view>
          </view>
        </view>
        <view class="cc-divider"></view>
        <view class="cc-row">
          <view class="cc-r-icon">📍</view>
          <text class="cc-r-text">{{ order.address||'待确认' }}</text>
          <text class="cc-action-text" @click="copyText(order.address,'地址')">复制</text>
          <view class="cc-nav-btn" @click="openMap('amap')">导航</view>
        </view>
        <view class="cc-row" v-if="order.appointment_time">
          <view class="cc-r-icon">📅</view>
          <text class="cc-r-text">预约 {{ (order.appointment_time||'').replace('T',' ').slice(0,16) }}</text>
        </view>
        <view class="cc-row" v-else>
          <view class="cc-r-icon">🕐</view>
          <text class="cc-r-text">{{ order.created_at ? order.created_at.slice(0,10)+' '+order.created_at.slice(11,16) : '' }}</text>
        </view>
      </view>

      <!-- 客户历史 -->
      <view class="section-card" v-if="customerHistory.length">
        <view class="section-title">
          <text>客户历史</text>
          <text class="section-badge">{{ customerHistory.length }}次服务</text>
        </view>
        <view v-for="(h, i) in customerHistory.slice(0, 5)" :key="h.id" class="history-item" @click="goDetail(h.id)">
          <view class="hi-header">
            <text class="hi-time">{{ h.created_at ? h.created_at.slice(0,10) : '' }}</text>
            <text :class="'hi-status ' + h.status">{{ statusLabel(h.status) }}</text>
          </view>
          <text class="hi-service">{{ h.service_item_name || '维修' }}</text>
          <text class="hi-fee" v-if="h.total_fee">¥{{ h.total_fee }}</text>
        </view>
      </view>

      <!-- Service Info -->
      <view class="section-card">
        <view class="section-title">服务信息</view>
        <view class="detail-row">
          <text class="detail-label">服务项目</text>
          <text class="detail-val-primary">{{ order.service_item_name||'-' }}</text>
        </view>
        <view class="detail-row">
          <text class="detail-label">分类</text>
          <text class="detail-value">{{ order.category_type||'-' }}</text>
        </view>
        <view class="detail-row" v-if="order.fault_description">
          <text class="detail-label">故障描述</text>
          <text class="detail-fault">{{ order.fault_description }}</text>
        </view>
      </view>

      <!-- Income & Payment -->
      <view class="income-section" v-if="order.total_fee||order.service_fee">
        <view class="income-title">费用明细</view>
        <view class="income-row"><text class="il">服务费</text><text class="ir">¥{{ order.service_fee||0 }}</text></view>
        <view class="income-row" v-if="order.material_fee"><text class="il">材料费</text><text class="ir">¥{{ order.material_fee }}</text></view>
        <view class="income-row" v-if="orderParts.length"><text class="il">配件费</text><text class="ir">¥{{ orderParts.reduce((s,p)=>s+(p.total_price||0),0) }}</text></view>
        <view class="income-divider"></view>
        <view class="income-row income-total"><text class="il il-bold">服务总费用</text><text class="ir-total">¥{{ order.total_fee||order.service_fee||0 }}</text></view>
        <view class="income-row income-net"><text class="il il-sm">实收入（已扣除平台费）</text><text class="ir-net">¥{{ ((order.total_fee||order.service_fee||0) * 0.8).toFixed(1) }}</text></view>
        <view class="income-row income-foot" v-if="order.pay_status==='paid'">
          <text class="il il-sm">收款方式：{{ order.payment_method==='cash'?'现金':order.payment_method==='wechat'?'微信':order.payment_method==='alipay'?'支付宝':'转账' }}</text>
          <text class="il-sm" style="color:var(--text-tertiary)">{{ (order.paid_at||'').slice(0,16)||'' }}</text>
        </view>
        <view class="income-row income-foot" v-else-if="order.status==='completed'||order.status==='done'">
          <text class="il-pending">待收款 — 请提醒客户付款</text>
        </view>
      </view>

      <!-- Parts -->
      <view class="section-card" v-if="orderParts.length">
        <view class="section-title"><text>配件材料</text><text class="section-badge">{{ orderParts.length }}项</text></view>
        <view v-for="(p,i) in orderParts" :key="p.id" class="part-item">
          <view class="part-top"><text class="part-name">{{ p.name }}</text><text class="part-qty">x{{ p.quantity }}</text></view>
          <view class="part-bottom"><text class="part-price">¥{{ p.unit_price }}/个</text><text class="part-total">= ¥{{ p.total_price }}</text></view>
          <view class="part-meta" v-if="p.store_name||p.receipt_image||p.part_photo">
            <text v-if="p.store_name">{{ p.store_name }}</text>
            <text v-if="p.store_phone">{{ p.store_phone }}</text>
            <text v-if="p.receipt_image" class="link" @click="previewImage(p.receipt_image)">票据</text>
            <text v-if="p.part_photo" class="link" style="color:var(--success)" @click="previewImage(p.part_photo)">照片</text>
          </view>
        </view>
      </view>

      <!-- Quote -->
      <view class="section-card" v-if="order.quote_status">
        <view class="section-title"><text>报价信息</text><text :class="'quote-badge '+order.quote_status">{{ order.quote_status==='pending'?'待客户确认':order.quote_status==='accepted'?'客户已接受':order.quote_status==='rejected'?'客户已拒绝':'' }}</text></view>
        <view class="qi-box" v-if="quoteItems.length">
          <view class="qi-row" v-for="(item,i) in quoteItems" :key="i">
            <view class="qi-left"><text class="qi-name">{{ item.name }}</text><text class="qi-detail">x{{ item.quantity }} 个 · ¥{{ item.unit_price }}/个</text></view>
            <text class="qi-subtotal">¥{{ (item.quantity||1)*(item.unit_price||0) }}</text>
          </view>
        </view>
        <view class="qi-summary" v-if="order.service_fee || order.material_fee">
          <view class="qi-fee" v-if="order.service_fee"><text>服务费</text><text>¥{{ order.service_fee }}</text></view>
          <view class="qi-fee" v-if="order.material_fee"><text>材料费</text><text>¥{{ order.material_fee }}</text></view>
        </view>
        <view class="qi-total"><text>合计</text><text class="qi-amount">¥{{ order.quote_amount||0 }}</text></view>
      </view>

      <!-- Trip Fee -->
      <view class="section-card" v-if="order.quote_status==='rejected'&&!order.trip_fee_status">
        <view class="section-title">上门费</view>
        <view class="trip-hint">客户拒绝报价，可收取上门检测费</view>
        <view class="trip-form">
          <text class="trip-label">金额</text>
          <input class="trip-input" type="digit" v-model="tripFeeAmount" />
          <text style="margin-left:4px;color:var(--text-tertiary)">元</text>
        </view>
        <button class="btn-trip" @click="chargeTripFee">收取上门费 ¥{{ tripFeeAmount }}</button>
      </view>

      <!-- Photos & Video -->
      <view class="section-card" v-if="order.before_photos||order.after_photos||order.video_url">
        <view class="section-title">维修影像</view>
        <view class="media-block" v-if="order.before_photos">
          <text class="media-label">维修前</text>
          <view class="media-grid">
            <view v-for="(p,i) in parsePhotos(order.before_photos)" :key="i" class="media-item" @click="previewImage(p)">
              <img :src="p" class="media-img" style="object-fit:cover;width:100%;height:100%">
            </view>
          </view>
        </view>
        <view class="media-block" v-if="order.after_photos">
          <text class="media-label">维修后</text>
          <view class="media-grid">
            <view v-for="(p,i) in parsePhotos(order.after_photos)" :key="i" class="media-item" @click="previewImage(p)">
              <img :src="p" class="media-img" style="object-fit:cover;width:100%;height:100%">
            </view>
          </view>
        </view>
        <view class="media-block" v-if="order.video_url">
          <text class="media-label">维修视频</text>
          <video :src="order.video_url" class="detail-video" controls :autoplay="false" @error="console.error('video error', $event)"></video>
        </view>
      </view>

      <!-- Complete Form -->
      <view class="section-card" v-if="order.status==='in_progress'">
        <view class="section-title">上传完工照片</view>
        <view class="media-block">
          <text class="media-label">维修前照片</text>
          <view class="media-grid">
            <view v-for="(p,i) in captureBefore" :key="i" class="media-item"><img :src="p" class="media-img" style="object-fit:cover;width:100%;height:100%"><text class="media-del" @click="captureBefore.splice(i,1)">✕</text></view>
            <view class="media-add" @click="takePhoto('before')"><text class="plus-icon">+</text><text class="media-add-label">拍照</text></view>
          </view>
        </view>
        <view class="media-block">
          <text class="media-label">维修后照片</text>
          <view class="media-grid">
            <view v-for="(p,i) in captureAfter" :key="i" class="media-item"><img :src="p" class="media-img" style="object-fit:cover;width:100%;height:100%"><text class="media-del" @click="captureAfter.splice(i,1)">✕</text></view>
            <view class="media-add" @click="takePhoto('after')"><text class="plus-icon">+</text><text class="media-add-label">拍照</text></view>
          </view>
        </view>
        <view class="video-row">
          <text class="video-btn" @click="recordVideo">补充视频佐证</text>
          <text v-if="captureVideo" class="video-done">已录制</text>
        </view>
      </view>

      <!-- Action Bar -->
      <view class="action-bar" v-if="showActions">
        <view class="action-steps">
          <view class="action-row" v-if="order.status==='pending'||order.status==='dispatched'||(order.status==='accepted' && !order.technician_id)">
            <button class="action-btn action-primary" @click="acceptOrder">
              {{ order.status==='accepted'?'抢单':'接单' }}
            </button>
            <button class="action-btn action-outline" @click="showReject=true">无法接单</button>
          </view>
          <template v-if="order.status==='accepted' && order.technician_id">
            <button class="action-btn action-blue" @click="callCustomer" v-if="!contacted">联系客户</button>
            <template v-if="contacted && !verified">
              <button class="action-btn action-primary" @click="showDatePicker=true" v-if="!order.appointment_time">📅 预约上门时间</button>
              <view class="action-schedule" v-if="order.appointment_time">
                <text>📅 {{ order.appointment_time.slice(5,10) }} {{ order.appointment_time.slice(11,16) }} 上门</text>
                <text class="action-reschedule" @click="showDatePicker=true">改期</text>
              </view>
              <button class="action-btn action-primary" @click="goToDoor">📍 我已到达</button>
            </template>
            <button class="action-btn action-green" @click="startServiceAfterVerify" v-if="verified">开始服务</button>
            <button class="action-btn action-danger-text" @click="showReject=true" v-if="!verified">没时间去 · 申请取消</button>
            <button class="action-btn action-transfer-text" @click="showTransfer=true" v-if="order.status==='accepted'">转给其他师傅</button>
          </template>
          <button class="action-btn action-yellow" @click="doQuote" v-if="order.status==='in_progress' && !order.quote_status">报价</button>
          <button class="action-btn action-green" @click="quoteOptions" v-if="order.status==='in_progress' && order.quote_status==='pending'">客户确认报价 (¥{{ order.quote_amount||0 }})</button>
          <button class="action-btn action-yellow" @click="doQuote" v-if="order.status==='in_progress' && order.quote_status==='rejected'">重新报价</button>
          <button class="action-btn action-primary" @click="startRepair" v-if="order.status==='in_progress' && order.quote_status==='accepted' && !repairStarted">确认维修</button>
          <button class="action-btn action-green" @click="finishWork" v-if="order.status==='in_progress' && order.quote_status==='accepted' && repairStarted">完工</button>
          <button class="action-btn action-yellow" @click="showPayOptions" v-if="(order.status==='completed'||order.status==='done') && order.pay_status!=='paid'">收款 ¥{{ order.total_fee||order.service_fee||0 }}</button>
          <view class="action-paid" v-if="(order.status==='paid')">已收款</view>
        </view>
      </view>

      <view class="bottom-spacer"></view>

      <!-- 日期选择弹窗 -->
      <view class="modal-overlay" v-if="showDatePicker" @click="showDatePicker=false">
        <view class="schedule-box" @click.stop>
          <view class="schedule-header">📅 预约上门时间</view>
          <view class="schedule-row">
            <text class="schedule-label">日期</text>
            <input type="date" :value="pickerDate" @change="e=>pickerDate=e.target.value" style="flex:1;padding:8px 12px;border:1px solid var(--border,#e8e8e8);border-radius:8px;font-size:15px" />
          </view>
          <view class="schedule-row">
            <text class="schedule-label">时间</text>
            <input type="time" :value="pickerTime" @change="e=>pickerTime=e.target.value" style="flex:1;padding:8px 12px;border:1px solid var(--border,#e8e8e8);border-radius:8px;font-size:15px" />
          </view>
          <view class="schedule-actions">
            <button class="schedule-btn schedule-cancel" @click="showDatePicker=false">取消</button>
            <button class="schedule-btn schedule-confirm" @click="confirmSchedule">确定</button>
          </view>
        </view>
      </view>

      <!-- 验证弹窗 -->
      <view class="modal-overlay" v-if="showVerify" @click="showVerify=false">
        <view class="verify-box" @click.stop>
          <view class="verify-header">确认已到达</view>
          <view class="verify-addr">{{ order.customer_name||'客户' }} · {{ (order.address||'').slice(0,20) }}</view>
          <view class="verify-hint">请输入客户手机号后4位验证</view>
          <input class="verify-input" type="tel" maxlength="4" v-model="verifyCode" placeholder="...." @confirm="doVerify"/>
          <view class="verify-actions">
            <button class="verify-btn verify-cancel" @click="showVerify=false">取消</button>
            <button class="verify-btn verify-confirm" @click="doVerify">确认到达</button>
          </view>
        </view>
      </view>

      <!-- 评价弹窗 -->
      <view class="modal-overlay" v-if="showRate" @click="showRate=false">
        <view class="rmodal" @click.stop>
          <view class="rate-title">客户评价</view>
          <view class="rate-body">
            <text class="rate-hint">为本次服务打分</text>
            <view class="rate-stars">
              <text v-for="s in 5" :key="s" @click="rateScore=s" :class="'rate-star '+(s<=rateScore?'active':'')">{{ s<=rateScore?'★':'☆' }}</text>
            </view>
          </view>
          <input class="rate-input" type="text" v-model="rateComment" placeholder="写点评价（选填）" />
          <view class="rate-actions">
            <button class="rate-btn rate-skip" @click="showRate=false">跳过</button>
            <button class="rate-btn rate-submit" @click="doRate">提交评价</button>
          </view>
        </view>
      </view>

      <!-- 拒单弹窗 -->
      <view class="modal-overlay" v-if="showReject" @click="showReject=false">
        <view class="rmodal" @click.stop>
          <view class="rate-title">申请取消工单</view>
          <text class="reject-hint">说明取消原因，管理员审核后将重新派单</text>
          <select :value="rejectReasonIndex" @change="e=>{const i=parseInt(e.target.value);rejectReasonIndex=i;rejectReason=rejectReasons[i]}" style="width:100%;margin-bottom:12px;padding:10px 12px;border:1.5px solid var(--border,#e8e8e8);border-radius:10px;font-size:15px;background:var(--bg-fill,#f8f9fb)">
            <option value="-1" disabled>请选择原因</option>
            <option v-for="(r,i) in rejectReasons" :key="i" :value="i">{{ r }}</option>
          </select>
          <input class="rate-input" type="text" v-model="rejectReason" placeholder="或手动输入原因..." />
          <view class="rate-actions">
            <button class="rate-btn rate-skip" @click="showReject=false">再想想</button>
            <button class="rate-btn rate-submit" style="background:var(--danger)" @click="doReject">确认取消</button>
          </view>
        </view>
      </view>

      <!-- 转单弹窗 -->
      <view class="modal-overlay" v-if="showTransfer" @click="showTransfer=false">
        <view class="rmodal" @click.stop>
          <view class="rate-title">转给其他师傅</view>
          <text class="reject-hint" v-if="transferTechs.length===0">加载师傅列表...</text>
          <view style="max-height:320px;overflow-y:auto;margin-bottom:12px" v-else>
            <view
              v-for="tech in transferTechs" :key="tech.id"
              :class="'transfer-item '+(transferTargetId===tech.id?'transfer-active':'')"
              @click="transferTargetId=tech.id"
            >
              <view class="transfer-left">
                <view class="transfer-avatar">{{ (tech.name||'?').charAt(0) }}</view>
                <view class="transfer-info">
                  <text class="transfer-name">{{ tech.name }}</text>
                  <text class="transfer-detail">{{ tech.skills?.length||0 }}项技能 · {{ tech.active_orders||0 }}个进行中</text>
                </view>
              </view>
              <text class="transfer-check" v-if="transferTargetId===tech.id">✓</text>
            </view>
          </view>
          <input class="rate-input" type="text" v-model="transferReason" placeholder="转单原因（选填）" />
          <view class="rate-actions">
            <button class="rate-btn rate-skip" @click="showTransfer=false">取消</button>
            <button class="rate-btn rate-submit" :disabled="!transferTargetId" @click="doTransfer">确认转单</button>
          </view>
        </view>
      </view>
    </view>
  </view>

</template>
<script>
import api from '../../api'
const UPLOAD_URL = ((typeof process !== 'undefined' && process.env?.VITE_API_BASE) || 'https://zpqy.cn/api') + '/upload'
export default {
  data() { return { order: null, loading: true, orderId: null, orderParts: [], customerHistory: [], tripFeeAmount: 30, captureBefore: [], captureAfter: [], captureVideo: null, _callRecorder: null, _callRecordingPath: null, showVerify: false, verifyCode: '', showRate: false, rateScore: 5, rateComment: '', verified: false, contacted: false, repairStarted: false, quoteItems: [], showDatePicker: false, pickerDate: '', pickerTime: '', showReject: false, rejectReason: '', rejectReasonIndex: -1, rejectReasons: ['时间冲突，无法上门', '距离太远，无法前往', '技能不匹配，无法维修', '客户态度问题', '个人原因', '其他'], showTransfer: false, transferTechs: [], transferTargetId: null, transferReason: '' } },
  onLoad(q) { this.orderId = q.id; setTimeout(()=>this.loadOrder(),100) },
  onShow() { if(this.orderId)this.loadOrder() },
  watch: {
    showTransfer(val) { if (val) { this.transferTargetId = null; this.transferReason = ''; this.loadTransferTechs() } }
  },
  computed: {
    showActions() { const s = this.order?.status; return !!s && s!=='cancelled' },
    showTimeline() {
      const s = this.order?.status
      return s && ['accepted','in_progress','completed','done','paid'].includes(s)
    },
    timelineSteps() {
      const flow = ['dispatched','accepted','in_progress','completed','paid']
      const labels = ['已派单','已接单','服务中','已完工','已付款']
      const cur = flow.indexOf(this.order?.status)
      return labels.map((label, i) => ({ label, done: i <= cur }))
    }
  },
  methods: {
    statusIcon(s) { return s==='pending'||s==='dispatched'?'📋':s==='accepted'?'🔧':s==='in_progress'?'⚡':s==='completed'||s==='done'||s==='paid'?'✅':s==='CANCEL_PENDING'?'⏳':'❌' },
    statusLabel(s) { const m={pending:'待接单',dispatched:'已派单',accepted:'已接单',in_progress:'进行中',completed:'已完成',paid:'已付款',done:'已完成',cancelled:'已取消',CANCEL_PENDING:'待审核'}; return m[s]||s },
    async rejectOrder() {
      uni.showModal({ title:'取消订单', content:'确认取消？需平台审核', success:async(r)=>{
        if(r.confirm){ try{await api.rejectOrder(this.orderId);uni.showToast({title:'已提交取消申请'});setTimeout(()=>uni.navigateBack(),500)}catch(e){uni.showToast({title:typeof e==='string'?e:'操作失败',icon:'none'})} }
      }})
    },
    async doReject() {
      if (!this.rejectReason || !this.rejectReason.trim()) { uni.showToast({ title:'请选择或输入取消原因', icon:'none' }); return }
      try {
        const res = await api.rejectOrder(this.orderId, this.rejectReason)
        this.showReject = false
        uni.showToast({ title: res?.message || '已提交' })
        setTimeout(() => uni.navigateBack(), 800)
      } catch(e) { uni.showToast({ title: e.message || '操作失败', icon:'none' }) }
    },
    async loadTransferTechs() {
      try {
        const res = await api.getTechList()
        const all = Array.isArray(res.data) ? res.data : []
        this.transferTechs = all.filter(t => t.id !== this.user?.id && t.status === 'active')
      } catch(e) { uni.showToast({ title: '加载师傅列表失败', icon:'none' }) }
    },
    async doTransfer() {
      if (!this.transferTargetId) { uni.showToast({ title:'请选择目标师傅', icon:'none' }); return }
      try {
        const res = await api.transferOrder(this.orderId, {
          technician_id: this.transferTargetId,
          reason: this.transferReason || '',
        })
        this.showTransfer = false
        uni.showToast({ title: res?.message || '转单成功' })
        this.loadOrder()
      } catch(e) { uni.showToast({ title: e.message || '转单失败', icon:'none' }) }
    },
    async loadOrder() {
      try {
        const [orderRes, partsRes] = await Promise.all([
          api.getOrderDetail(this.orderId),
          api.getParts(this.orderId).catch(()=>({data:[]}))
        ])
        this.order = orderRes.data?.order || orderRes.data
        this.orderParts = partsRes.data || []
        this.repairStarted = uni.getStorageSync('rs_' + this.orderId) === true
        this.contacted = uni.getStorageSync('rs_contacted_' + this.orderId) === true
        if (this.order?.quote_status) { await this.loadQuote() }
        // 加载客户历史
        this.loadCustomerHistory()
      } catch(e) { uni.showToast({ title:'加载失败', icon:'none' }) }
      finally { this.loading = false }
    },
    async loadCustomerHistory() {
      if (!this.order?.customer_id) return
      try {
        const user = uni.getStorageSync('user')
        if (user?.id) {
          const res = await api.getCustomerHistory(this.order.customer_id, user.id)
          this.customerHistory = (res.data || []).filter(o => o.id !== this.orderId)
        }
      } catch(e) {}
    },
    async loadQuote() {
      if (!this.orderId) return
      try { const res = await api.getQuote(this.orderId); if (res.data?.quote_items) { this.quoteItems = res.data.quote_items } } catch(e) {}
    },
    async acceptOrder() { try { await api.acceptOrder(this.orderId, uni.getStorageSync('user').id); uni.showToast({ title:'已接单' }); this.loadOrder() } catch(e) { uni.showToast({ title:typeof e==='string'?e:'操作失败', icon:'none' }) } },
    callCustomer() {
      const phone = this.order.customer_phone
      if (!phone) { uni.showToast({ title:'暂无客户电话', icon:'none' }); return }
      try { const rm = uni.getRecorderManager(); rm.onStop((res) => { this._callRecordingPath = res.tempFilePath }); rm.onError(()=>{}); rm.start({ format: 'mp3' }); this._callRecorder = rm } catch(e) {}
      uni.showModal({ title:'呼叫客户', content:`拨打 ${phone.slice(0,3)}****${phone.slice(-4)}？`, success: (r) => { if (r.confirm) uni.makePhoneCall({ phoneNumber: phone, fail:()=>{} }); this.contacted = true; uni.setStorageSync('rs_contacted_' + this.orderId, true); this.loadOrder() } })
    },
    smsCustomer() {
      const phone = this.order.customer_phone
      if (!phone) { uni.showToast({ title:'暂无客户电话', icon:'none' }); return }
      uni.showModal({ title:'发送短信', content:`向 ${phone.slice(0,3)}****${phone.slice(-4)} 发送短信？`, success: (r) => { if (r.confirm && typeof plus !== 'undefined') { plus.runtime.openURL('sms:' + phone) } } })
    },
    goToDoor() { this.showVerify = true },
    confirmSchedule() {
      if (!this.pickerDate) { uni.showToast({ title:'请选择日期', icon:'none' }); return }
      const t = this.pickerTime || '09:00'
      const fullTime = this.pickerDate + 'T' + t + ':00'
      this.order.appointment_time = fullTime.replace('T',' ').slice(0,16)
      uni.request({ url: 'https://zpqy.cn/api/orders/' + this.orderId, method: 'PUT', header: { 'Authorization': 'Bearer ' + uni.getStorageSync('token'), 'Content-Type': 'application/json' }, data: { appointment_time: fullTime }, fail: () => {} })
      this.showDatePicker = false
      uni.showToast({ title:'上门时间已设置', icon:'none' })
    },
    async doVerify() {
      if (!this.verifyCode || this.verifyCode.length !== 4) { uni.showToast({ title:'请输入4位手机尾号', icon:'none' }); return }
      try { await api.verifyCustomer(this.orderId, this.verifyCode); this.showVerify = false; this.verified = true; uni.showToast({ title:'客户验证通过' }) } catch(e) { uni.showToast({ title: e.message || '验证失败', icon:'none' }) }
    },
    async startServiceAfterVerify() { try { await api.startService(this.orderId, uni.getStorageSync('user').id); uni.showToast({ title:'已开始服务' }); this.loadOrder() } catch(e) { uni.showToast({ title: e.message || '操作失败', icon:'none' }) } },
    startRepair() { this.repairStarted = true; uni.setStorageSync('rs_' + this.orderId, true) },
    quoteOptions() {
      uni.showActionSheet({
        itemList: ['✅ 客户已同意', '❌ 客户不同意', '⏳ 客户考虑一下', '🚫 客户确定不需要'],
        success: (r) => {
          if (r.tapIndex === 0) {
            // 客户已同意
            uni.showModal({ title:'确认报价', content:'确认客户已接受 ¥' + (this.order.quote_amount||0) + ' 的报价？', success: async (r2) => {
              if (r2.confirm) { try { await api.respondQuote(this.orderId, 'accept'); uni.showToast({ title:'报价已确认' }); this.loadOrder() } catch(e) { uni.showToast({ title:'操作失败', icon:'none' }) } }
            }})
          } else if (r.tapIndex === 1) {
            // 客户不同意报价
            uni.showModal({ title:'取消订单', content:'客户不同意报价，确认取消此工单？', success: async (r2) => {
              if (r2.confirm) { try { await api.respondQuote(this.orderId, 'reject'); uni.showToast({ title:'已取消' }); this.loadOrder() } catch(e) { uni.showToast({ title:'操作失败', icon:'none' }) } }
            }})
          } else if (r.tapIndex === 2) {
            // 客户考虑一下
            uni.showToast({ title:'已标记"客户考虑中"，请稍后跟进', icon:'none' })
          } else {
            // 客户确定不需要
            uni.showModal({ title:'取消订单', content:'客户确定不需要此服务，确认取消工单？（需平台审核）', success: async (r2) => {
              if (r2.confirm) { try { await api.rejectOrder(this.orderId, '客户不需要'); uni.showToast({ title:'已提交取消申请' }); setTimeout(()=>uni.navigateBack(),500) } catch(e) { uni.showToast({ title:'操作失败', icon:'none' }) } }
            }})
          }
        }
      })
    },
    async finishWork() {
      try { if (this._callRecorder) { try { this._callRecorder.stop() } catch(e) {} }; let audioUrl = null; if (this._callRecordingPath) { try { audioUrl = await this.uploadFile(this._callRecordingPath) } catch(e) {} }; await api.completeOrder(this.orderId, { before_photos: this.captureBefore.length ? JSON.stringify(this.captureBefore) : null, after_photos: this.captureAfter.length ? JSON.stringify(this.captureAfter) : null, video_url: this.captureVideo || null, audio_url: audioUrl }); uni.removeStorageSync('rs_' + this.orderId); uni.showToast({ title:'完工成功' }); this.loadOrder(); this.showRate = true } catch(e) { uni.showToast({ title: e.message || '完工提交失败', icon:'none' }) }
    },
    addPart() { uni.navigateTo({ url:'/pages/orders/quote?id='+this.orderId+'&parts=1' }) },
    previewImage(src) { let group = this.parsePhotos(this.order.before_photos||''); let isBefore = group.some(p => p === src || src.includes(p) || p.includes(src)); if (!isBefore) group = this.parsePhotos(this.order.after_photos||''); uni.previewImage({ urls: group.length ? group : [src], current: src }) },
    parsePhotos(str) { try{return JSON.parse(str)}catch(e){return str?[str]:[]} },
    takePhoto(type) { uni.chooseImage({ count: 3, sizeType:['compressed'], sourceType:['camera'], success: async (r) => { uni.showLoading({ title: '上传照片中...' }); const urls = []; for (const p of r.tempFilePaths) { try { urls.push(await this.uploadFile(p)) } catch(e) { console.error('照片上传失败', e) } }; if (type === 'before') this.captureBefore = this.captureBefore.concat(urls); else this.captureAfter = this.captureAfter.concat(urls); uni.hideLoading() }}) },
    recordVideo() { uni.chooseVideo({ sourceType:['camera'], maxDuration:30, success: async (r) => { try { this.captureVideo = await this.uploadFile(r.tempFilePath); uni.showToast({ title:'视频上传成功' }) } catch(e) { uni.showToast({ title:'视频上传失败', icon:'none' }) } }}) },
    uploadFile(filePath) { return new Promise((resolve, reject) => { const token = uni.getStorageSync('token'); uni.uploadFile({ url: UPLOAD_URL, filePath, name: 'file', header: token ? { 'Authorization': `Bearer ${token}` } : {}, success: (res) => { try { const data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data; if (data?.data?.url) resolve('https://zpqy.cn' + data.data.url); else reject('上传返回数据异常') } catch(e) { reject('解析上传结果失败') } }, fail: () => reject('上传失败，请检查网络') }) }) },
    copyText(text, label) { if (!text) { uni.showToast({ title:'暂无'+label, icon:'none' }); return }; uni.setClipboardData({ data: text, success: () => uni.showToast({ title:label+'已复制' }) }) },
    openMap(type) {
      const addr = this.order.address || ''; const lat = this.order.latitude; const lng = this.order.longitude
      if (typeof plus !== 'undefined') {
        if (type === 'amap') { const url = lat && lng ? `https://uri.amap.com/navigation?to=${lng},${lat},${encodeURIComponent(addr)}&mode=car&coordinate=gaode` : `https://uri.amap.com/navigation?to=0,0,${encodeURIComponent(addr)}&mode=car`; plus.runtime.openURL(url, err => { uni.showToast({ title:'请安装高德地图', icon:'none' }) }) }
        else { const url = lat && lng ? `https://apis.map.qq.com/uri/v1/navi?car=${lat},${lng}&coord_type=gcj02` : `https://apis.map.qq.com/uri/v1/search?keyword=${encodeURIComponent(addr)}`; plus.runtime.openURL(url, err => { uni.showToast({ title:'请安装腾讯地图', icon:'none' }) }) }
      } else if (lat && lng) { uni.showToast({ title:'仅支持 App 端打开地图导航', icon:'none' }) } else { uni.showToast({ title:'暂无位置信息', icon:'none' }) }
    },
    async doRate() { try{ await api.rateOrder(this.orderId, this.rateScore, this.rateComment); this.showRate=false; uni.showToast({title:'评价成功'}); this.loadOrder() } catch(e){ uni.showToast({title:'提交失败',icon:'none'}) } },
    doQuote() { uni.navigateTo({ url: `/pages/orders/quote?id=${this.orderId}&no=${this.order.order_no}` }) },
    showPayOptions() {
      if (this.order.pay_status === 'paid') { uni.showToast({ title: '已收款', icon: 'none' }); return }
      const amount = this.order.total_fee || this.order.service_fee || 0
      uni.showActionSheet({
        itemList: ['💰 现金 ¥' + amount, '💚 微信 ¥' + amount, '💙 支付宝 ¥' + amount],
        success: (r) => {
          const methods = ['cash', 'wechat', 'alipay']
          this.markAsPaid(methods[r.tapIndex])
        },
        fail: () => { uni.showToast({ title: '已取消', icon: 'none' }) }
      })
    },
    async markAsPaid(method) { try { await api.markPaid(this.orderId, { payment_method: method }); uni.showToast({ title: '已标记收款' }); this.loadOrder() } catch(e) { uni.showToast({ title: e.message, icon:'none' }) } },
    async chargeTripFee() {
      if (this.tripFeeAmount <= 0) { uni.showToast({ title:'请输入有效金额', icon:'none' }); return }
      uni.showModal({ title:'确认收费', content:'¥' + this.tripFeeAmount + '？', success: async (r) => {
        if (r.confirm) { try { await api.chargeTripFee(this.orderId, { amount: Number(this.tripFeeAmount), remark: '' }); uni.showToast({ title: '上门费已收取' }); this.loadOrder() } catch(e) { uni.showToast({ title: e.message, icon:'none' }) } }
      }})
    }
  }
}
</script>

<style>
/* ========== Layout ========== */
.page{background:var(--bg-page);min-height:100vh;width:100%;overflow-x:hidden;box-sizing:border-box}
.skeleton-wrap{padding:var(--spacing-lg)}.detail-wrap{padding-bottom:0}

/* ========== Status Header ========== */
.status-header{display:flex;justify-content:space-between;align-items:center;padding:var(--spacing-lg);color:#fff}
.status-header.pending,.status-header.dispatched{background:linear-gradient(135deg,#fa8c16,#d46b08)}
.status-header.accepted{background:var(--primary-gradient)}
.status-header.in_progress{background:linear-gradient(135deg,#d48806,#ad8b00)}
.status-header.completed,.status-header.done,.status-header.paid{background:linear-gradient(135deg,var(--success),#389e0d)}
.status-header.cancelled{background:linear-gradient(135deg,#999,#666)}
.status-header.CANCEL_PENDING{background:linear-gradient(135deg,#f5a623,#e67e22)}
.status-left{display:flex;align-items:center;gap:var(--spacing-md)}
.status-icon-circle{width:40px;height:40px;border-radius:50%;background:rgba(255,255,255,.2);display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0}
.status-title{font-size:var(--font-xl);font-weight:700}
.order-no{font-size:var(--font-sm);opacity:.8;margin-top:2px;display:block}
.status-time{font-size:var(--font-sm);opacity:.7}
.copy-btn{font-size:var(--font-sm);color:#fff;opacity:.7;margin-top:2px;display:inline-block;text-decoration:underline}

/* ========== Timeline ========== */
.timeline-wrap{display:flex;justify-content:center;padding:var(--spacing-lg) var(--spacing-lg) 0;gap:0;background:var(--bg-card);margin:0}
.tl-step{display:flex;flex-direction:column;align-items:center;position:relative;flex:1}
.tl-dot{width:10px;height:10px;border-radius:50%;margin-bottom:4px;position:relative;z-index:1}
.tl-done .tl-dot{background:var(--success);box-shadow:0 0 0 3px var(--success-bg)}
.tl-pending .tl-dot{background:var(--border-strong)}
.tl-label{font-size:10px;color:var(--text-tertiary);white-space:nowrap}
.tl-done .tl-label{color:var(--success);font-weight:600}
.tl-line{position:absolute;top:5px;right:-50%;width:100%;height:2px;background:var(--border-strong);z-index:0}
.tl-line-done{background:var(--success)}

/* ========== Customer Card ========== */
.customer-card{background:var(--bg-card);border-radius:var(--radius-lg);margin:var(--spacing-md) var(--spacing-lg);overflow:hidden;box-shadow:var(--shadow-sm);border:1px solid var(--border)}
.cc-top{display:flex;align-items:center;padding:var(--spacing-lg);gap:var(--spacing-md)}
.cc-avatar{width:44px;height:44px;border-radius:50%;background:var(--primary-gradient);color:#fff;display:flex;align-items:center;justify-content:center;font-size:var(--font-xl);font-weight:600;flex-shrink:0;box-shadow:0 2px 8px rgba(230,122,46,0.3)}
.cc-info{flex:1}
.cc-name{font-size:var(--font-lg);font-weight:600;display:block;color:var(--text-primary)}
.cc-phone{font-size:var(--font-base);color:var(--text-tertiary);margin-top:2px;display:block}
.cc-actions{display:flex;gap:var(--spacing-sm)}
.cc-icon{width:36px;height:36px;border-radius:50%;background:var(--bg-fill);display:flex;align-items:center;justify-content:center;font-size:var(--font-xl)}
.cc-divider{height:1px;background:var(--border);margin:0 var(--spacing-lg)}
.cc-row{display:flex;align-items:center;padding:var(--spacing-md) var(--spacing-lg);gap:var(--spacing-sm)}
.cc-r-icon{font-size:var(--font-lg);width:20px;text-align:center;flex-shrink:0}
.cc-r-text{flex:1;font-size:var(--font-base);color:var(--text-primary)}
.cc-action-text{font-size:var(--font-sm);color:var(--primary);padding:2px 6px}
.cc-nav-btn{font-size:var(--font-sm);color:#fff;background:var(--primary-gradient);padding:4px 10px;border-radius:var(--radius-sm);font-weight:500}

/* ========== Section Card ========== */
.section-card{background:var(--bg-card);border-radius:var(--radius-md);padding:var(--spacing-lg);margin:var(--spacing-md) var(--spacing-lg);box-shadow:var(--shadow-sm);border:1px solid var(--border)}
.section-title{font-size:var(--font-lg);font-weight:600;margin-bottom:var(--spacing-md);color:var(--text-primary);display:flex;justify-content:space-between;align-items:center}
.section-badge{font-size:var(--font-sm);background:var(--primary-light);color:var(--primary);padding:2px 8px;border-radius:var(--radius-sm);font-weight:500}
/* 客户历史 */
.history-item{display:flex;align-items:center;padding:var(--spacing-sm) 0;border-bottom:1px solid var(--border);gap:var(--spacing-sm)}
.history-item:last-child{border-bottom:none}
.history-item:active{opacity:.7}
.hi-header{display:flex;flex-direction:column;gap:2px;min-width:70px}
.hi-time{font-size:var(--font-sm);color:var(--text-tertiary)}
.hi-status{font-size:10px;padding:1px 6px;border-radius:var(--radius-sm);background:var(--bg-fill);color:var(--text-tertiary);text-align:center}
.hi-service{flex:1;font-size:var(--font-base);color:var(--text-primary)}
.hi-fee{font-size:var(--font-md);font-weight:600;color:var(--danger)}
.detail-row{margin-bottom:var(--spacing-sm);display:flex;flex-wrap:wrap}
.detail-label{font-size:var(--font-base);color:var(--text-tertiary);width:70px;flex-shrink:0;padding-top:2px}
.detail-value{font-size:var(--font-base);color:var(--text-primary);flex:1}
.detail-val-primary{font-size:var(--font-base);font-weight:600;color:var(--text-primary);flex:1}
.detail-fault{font-size:var(--font-base);color:var(--text-primary);background:var(--bg-fill);padding:var(--spacing-sm) var(--spacing-md);border-radius:var(--radius-sm);margin-top:4px;line-height:1.6;width:100%}

/* ========== Income Section ========== */
.income-section{background:var(--bg-card);border-radius:var(--radius-md);padding:var(--spacing-lg);margin:var(--spacing-md) var(--spacing-lg);box-shadow:var(--shadow-sm);border:1.5px solid var(--success-bg)}
.income-title{font-size:var(--font-lg);font-weight:600;margin-bottom:var(--spacing-md);color:var(--text-primary)}
.income-row{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--border)}
.income-divider{height:1px;background:var(--success-bg);margin:6px 0}
.income-total{border-color:var(--success-bg)!important;padding-bottom:10px!important;margin-bottom:4px}
.income-net{border:none!important;padding-top:6px}
.income-foot{border:none!important;padding-top:4px}
.il{font-size:var(--font-base);color:var(--text-secondary)}
.il-bold{font-weight:700;font-size:var(--font-lg)}
.il-sm{font-size:var(--font-sm);color:var(--text-tertiary)}
.il-pending{font-size:var(--font-sm);color:var(--warning)}
.ir{font-size:var(--font-base);color:var(--text-primary)}
.ir-total{color:var(--danger);font-size:var(--font-2xl);font-weight:700}
.ir-net{color:var(--success);font-size:var(--font-xl);font-weight:700}

/* ========== Parts ========== */
.part-item{padding:var(--spacing-md) 0;border-bottom:1px solid var(--border)}
.part-item:last-child{border-bottom:none}
.part-top{display:flex;align-items:center;gap:var(--spacing-sm);margin-bottom:4px}
.part-name{font-size:var(--font-base);font-weight:500;color:var(--text-primary)}
.part-qty{font-size:var(--font-sm);color:var(--text-tertiary)}
.part-bottom{display:flex;gap:var(--spacing-md)}
.part-price{font-size:var(--font-sm);color:var(--text-tertiary)}
.part-total{font-size:var(--font-base);font-weight:600;color:var(--danger)}
.part-meta{display:flex;gap:var(--spacing-md);margin-top:4px;font-size:var(--font-sm);color:var(--text-tertiary)}
.part-meta .link{color:var(--primary)}

/* ========== Quote ========== */
.quote-badge{font-size:var(--font-sm);padding:3px 10px;border-radius:var(--radius-sm);font-weight:500}
.quote-badge.pending{background:var(--warning-bg);color:#d48806}
.quote-badge.accepted{background:var(--success-bg);color:var(--success)}
.quote-badge.rejected{background:var(--danger-bg);color:var(--danger)}
.qi-box{background:var(--bg-fill);border-radius:var(--radius-sm);padding:4px 12px;margin-bottom:var(--spacing-sm)}
.qi-row{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--border)}
.qi-row:last-child{border-bottom:none}
.qi-left{flex:1}
.qi-name{font-size:var(--font-base);font-weight:500;display:block;color:var(--text-primary)}
.qi-detail{font-size:var(--font-sm);color:var(--text-tertiary);margin-top:2px;display:block}
.qi-subtotal{font-size:var(--font-md);font-weight:600;color:var(--primary)}
.qi-summary{background:var(--bg-fill);border-radius:var(--radius-sm);padding:8px 12px;margin-bottom:var(--spacing-sm)}
.qi-fee{display:flex;justify-content:space-between;font-size:var(--font-base);color:var(--text-secondary);padding:4px 0}
.qi-total{display:flex;justify-content:space-between;align-items:center;padding:10px 0 0;border-top:2px solid var(--border-strong);margin-top:4px;font-size:var(--font-md)}
.qi-amount{color:var(--danger);font-size:var(--font-2xl);font-weight:700}

/* ========== Trip Fee ========== */
.trip-hint{font-size:var(--font-base);color:var(--text-secondary);margin-bottom:var(--spacing-md);line-height:1.6}
.trip-form{display:flex;align-items:center;gap:var(--spacing-sm);margin-bottom:var(--spacing-md)}
.trip-label{font-size:var(--font-base);color:var(--text-primary)}
.trip-input{flex:1;max-width:120px;padding:10px 12px;border:1.5px solid var(--border-strong);border-radius:var(--radius-sm);font-size:var(--font-md);background:var(--bg-fill);text-align:center}
.btn-trip{width:100%;padding:14px;border:none;border-radius:var(--radius-sm);background:var(--primary-gradient);color:#fff;font-size:var(--font-lg);font-weight:600;margin-top:var(--spacing-sm)}

/* ========== Media ========== */
.media-block{margin-bottom:var(--spacing-md)}.media-block:last-child{margin-bottom:0}
.media-label{font-size:var(--font-base);font-weight:500;color:var(--text-secondary);display:block;margin-bottom:var(--spacing-xs)}
.media-grid{display:flex;gap:var(--spacing-sm);flex-wrap:wrap}
.media-item{width:80px;height:80px;border-radius:var(--radius-sm);overflow:hidden;position:relative;border:1px solid var(--border)}
.media-img{width:100%;height:100%;border-radius:var(--radius-sm)}
.media-del{position:absolute;top:2px;right:2px;width:18px;height:18px;border-radius:50%;background:rgba(0,0,0,.5);color:#fff;text-align:center;line-height:18px;font-size:12px}
.media-add{width:80px;height:80px;border:1.5px dashed var(--border-strong);border-radius:var(--radius-sm);display:flex;flex-direction:column;align-items:center;justify-content:center;background:var(--bg-fill)}
.plus-icon{font-size:28px;color:var(--text-tertiary)}
.media-add-label{font-size:var(--font-sm);color:var(--text-tertiary)}
.detail-video{width:100%;height:180px;border-radius:var(--radius-sm);margin-top:var(--spacing-xs)}
.video-row{display:flex;align-items:center;gap:var(--spacing-sm);margin-top:var(--spacing-md)}
.video-btn{font-size:var(--font-sm);color:var(--text-tertiary);text-decoration:underline}
.video-done{font-size:var(--font-sm);color:var(--success)}

/* ========== 底部操作栏 ========== */
.action-bar{position:fixed;bottom:0;left:0;right:0;padding:10px 16px calc(14px + env(safe-area-inset-bottom,0px));background:var(--bg-card);border-top:1px solid var(--border);box-shadow:0 -2px 10px rgba(0,0,0,.05);display:flex;justify-content:center;z-index:99}
.action-steps{width:100%;max-width:360px;display:flex;flex-direction:column;align-items:center}
.action-btn{width:100%;padding:12px;border:none;border-radius:var(--radius-sm);font-size:var(--font-lg);font-weight:600;color:#fff;text-align:center}
.action-primary{background:var(--primary-gradient)}
.action-green{background:linear-gradient(135deg,var(--success),#389e0d)}
.action-blue{background:var(--primary-gradient)}
.action-yellow{background:linear-gradient(135deg,var(--warning),#d48806)}
.action-paid{width:100%;padding:12px;border-radius:var(--radius-sm);font-size:var(--font-md);color:var(--text-tertiary);background:var(--bg-fill);text-align:center}
.bottom-spacer{height:80px}

/* ========== 验证弹窗 ========== */
.modal-overlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.4);z-index:100;display:flex;align-items:center;justify-content:center;padding:20px;backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px)}
@supports not (backdrop-filter:blur(4px)){.modal-overlay{backdrop-filter:none}}
/* 预约弹窗 */
.schedule-box{background:var(--bg-card);border-radius:var(--radius-lg);padding:var(--spacing-xl);width:100%;max-width:320px}
.schedule-header{font-size:var(--font-xl);font-weight:700;margin-bottom:var(--spacing-lg);text-align:center;color:var(--text-primary)}
.schedule-row{display:flex;align-items:center;gap:var(--spacing-md);margin-bottom:var(--spacing-md);padding:var(--spacing-sm) var(--spacing-md);background:var(--bg-fill);border-radius:var(--radius-sm)}
.schedule-label{font-size:var(--font-base);color:var(--text-secondary);width:50px;flex-shrink:0}
.schedule-picker{flex:1}
.schedule-val{font-size:var(--font-md);color:var(--primary);font-weight:500;padding:6px 0;display:block}
.schedule-actions{display:flex;gap:var(--spacing-sm);margin-top:var(--spacing-lg)}
.schedule-btn{flex:1;padding:var(--spacing-sm);border:none;border-radius:var(--radius-sm);font-size:var(--font-md);font-weight:600}
.schedule-cancel{background:var(--bg-fill);color:var(--text-secondary)}
.schedule-confirm{background:var(--primary-gradient);color:#fff}
/* 操作栏预约信息 */
.action-schedule{display:flex;align-items:center;gap:var(--spacing-sm);width:100%;padding:var(--spacing-sm);background:var(--bg-fill);border-radius:var(--radius-sm);font-size:var(--font-base);color:var(--text-secondary)}
.action-reschedule{font-size:var(--font-sm);color:var(--primary);margin-left:auto}
.verify-box{background:var(--bg-card);border-radius:var(--radius-lg);padding:var(--spacing-xl) var(--spacing-xl) var(--spacing-lg);width:100%;max-width:300px;text-align:center}
.verify-header{font-size:var(--font-xl);font-weight:700;margin-bottom:var(--spacing-xs);color:var(--text-primary)}
.verify-addr{font-size:var(--font-sm);color:var(--text-tertiary);margin-bottom:var(--spacing-md)}
.verify-hint{font-size:var(--font-base);color:var(--text-secondary);margin-bottom:var(--spacing-md)}
.verify-input{width:140px;padding:10px;border:2px solid var(--primary);border-radius:var(--radius-sm);font-size:24px;text-align:center;outline:none;background:var(--primary-light);letter-spacing:6px;font-weight:700;margin:0 auto var(--spacing-lg)}
.verify-actions{display:flex;gap:var(--spacing-sm)}
.verify-btn{flex:1;padding:10px;border:none;border-radius:var(--radius-sm);font-size:var(--font-md);font-weight:600}
.verify-cancel{background:var(--bg-fill);color:var(--text-secondary)}
.verify-confirm{background:var(--primary-gradient);color:#fff}

/* ========== 评价弹窗 ========== */
.rmodal{background:var(--bg-card);border-radius:var(--radius-lg);padding:24px;width:100%;max-width:320px}
.rate-title{font-size:var(--font-xl);font-weight:700;text-align:center;color:var(--text-primary)}
.rate-body{text-align:center;margin:var(--spacing-lg) 0}
.rate-hint{font-size:var(--font-base);color:var(--text-secondary);margin-bottom:var(--spacing-sm);display:block}
.rate-stars{display:flex;justify-content:center;gap:6px;font-size:32px}
.rate-star{color:var(--border-strong);cursor:pointer}
.rate-star.active{color:var(--warning)}
.rate-input{width:100%;padding:var(--spacing-md);border:2px solid var(--border);border-radius:var(--radius-sm);font-size:var(--font-base);outline:none;background:var(--bg-fill);box-sizing:border-box}
.rate-actions{display:flex;gap:var(--spacing-sm);margin-top:var(--spacing-lg)}
.rate-btn{flex:1;padding:12px;border:none;border-radius:var(--radius-sm);font-size:var(--font-md);font-weight:600}
.rate-skip{background:var(--bg-fill);color:var(--text-secondary)}
.rate-submit{background:var(--primary-gradient);color:#fff}
.reject-hint{font-size:var(--font-sm);color:var(--text-tertiary);text-align:center;margin:var(--spacing-sm) 0 var(--spacing-lg);display:block;line-height:1.5}
.reject-picker{width:100%;padding:var(--spacing-md);border:1.5px solid var(--border);border-radius:var(--radius-sm);font-size:var(--font-base);color:var(--text-primary);text-align:center;background:var(--bg-fill);margin-bottom:8px}
.action-row{display:flex;gap:var(--spacing-sm);width:100%}
.action-row .action-btn{flex:1}
.action-outline{background:transparent;border:1.5px solid var(--danger);color:var(--danger);padding:10px;border-radius:var(--radius-sm);font-size:var(--font-lg);font-weight:600;text-align:center}
.action-outline:active{background:var(--danger-bg)}
.action-danger-text{background:transparent;border:none;color:var(--danger);font-size:var(--font-sm);font-weight:400;padding:8px;text-align:center;width:100%;opacity:.7}
.action-danger-text:active{opacity:1}
.action-transfer-text{background:transparent;border:none;color:var(--info);font-size:var(--font-sm);font-weight:400;padding:8px;text-align:center;width:100%;opacity:.7}
.action-transfer-text:active{opacity:1}
.transfer-item{display:flex;align-items:center;justify-content:space-between;padding:var(--spacing-md);border-bottom:1px solid var(--border);transition:background .1s}
.transfer-item:active,.transfer-item.transfer-active{background:var(--primary-light)}
.transfer-left{display:flex;align-items:center;gap:var(--spacing-md);flex:1}
.transfer-avatar{width:36px;height:36px;border-radius:50%;background:var(--primary-gradient);color:#fff;display:flex;align-items:center;justify-content:center;font-size:var(--font-md);font-weight:600;flex-shrink:0}
.transfer-info{flex:1}
.transfer-name{font-size:var(--font-md);font-weight:500;color:var(--text-primary);display:block}
.transfer-detail{font-size:var(--font-sm);color:var(--text-tertiary);display:block;margin-top:2px}
.transfer-check{font-size:var(--font-xl);font-weight:700;color:var(--success);margin-left:var(--spacing-sm)}
</style>
