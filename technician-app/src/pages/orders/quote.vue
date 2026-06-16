<template>
  <view class="page">
    <view class="header-bar">
      <text class="back-btn" @click="goBack">‹ 返回</text>
      <text class="title-txt">现场报价</text>
      <text style="width:40px"></text>
    </view>

    <view class="order-ref">工单: {{ orderNo }}</view>

    <!-- 选择服务项目 -->
    <view class="section">
      <view class="sec-header">
        <text class="sec-title">添加维修项目</text>
        <text class="sec-hint">从常用项目中选择</text>
      </view>

      <view class="service-selector">
        <view class="ss-search" v-if="serviceItems.length > 5">
          <text class="ss-search-icon">🔍</text>
          <input class="ss-search-input" v-model="searchKeyword" placeholder="搜索项目..." />
        </view>
        <view class="ss-list" style="overflow-y:auto">
          <view
            v-for="item in filteredItems" :key="item.id"
            :class="'ss-item ' + (selectedServiceId === item.id ? 'ss-active' : '')"
            @click="selectService(item)"
          >
            <view class="ss-item-left">
              <text class="ss-item-name">{{ item.name }}</text>
              <text class="ss-item-unit">{{ item.unit_type || '次' }}</text>
            </view>
            <view class="ss-item-right">
              <text class="ss-item-price" v-if="item.default_price">¥{{ item.default_price }}</text>
              <text class="ss-item-add" v-if="selectedServiceId === item.id">✓</text>
            </view>
          </view>
        </view>
      </view>
      <button class="add-custom-btn" @click="addCustomItem">+ 手动输入项目</button>
    </view>

    <!-- 费用项目列表 -->
    <view class="section">
      <view class="sec-header">
        <text class="sec-title">费用项目</text>
        <text class="sec-count">{{ quoteItems.length }}项</text>
      </view>

      <view v-for="(item, i) in quoteItems" :key="i" class="quote-card">
        <view class="qc-top">
          <view class="qc-num">{{ i + 1 }}</view>
          <input class="qc-name" v-model="item.name" placeholder="项目名称" />
          <text class="qc-del" @click="removeItem(i)">✕</text>
        </view>
        <view class="qc-detail">
          <view class="qc-field">
            <text class="qc-label">数量</text>
            <input class="qc-input qty" type="number" v-model.number="item.quantity" />
          </view>
          <view class="qc-field">
            <text class="qc-label">单价(元)</text>
            <input class="qc-input price" type="digit" v-model.number="item.unit_price" />
          </view>
          <view class="qc-subtotal">
            <text class="qc-st-label">小计</text>
            <text class="qc-st-val">¥{{ (item.quantity||1)*(item.unit_price||0) }}</text>
          </view>
        </view>
      </view>

      <button class="add-btn" @click="showServiceSelector">+ 从项目库添加</button>
    </view>

    <view class="section">
      <view class="sec-header"><text class="sec-title">其他费用</text></view>
      <view class="fee-row">
        <text class="fee-label">服务费</text>
        <view class="fee-input-wrap">
          <input class="fee-input" type="digit" v-model.number="serviceFee" placeholder="0" />
          <text class="fee-unit">元</text>
        </view>
      </view>
      <view class="fee-row">
        <text class="fee-label">材料费</text>
        <view class="fee-input-wrap">
          <input class="fee-input" type="digit" v-model.number="materialFee" placeholder="0" />
          <text class="fee-unit">元</text>
        </view>
      </view>
    </view>

    <view class="total-card">
      <view class="total-left">
        <text class="total-label">报价合计</text>
        <text class="total-hint">含服务费、材料费及各项费用</text>
      </view>
      <text class="total-amount">¥{{ totalAmount }}</text>
    </view>

    <view class="bottom-bar">
      <button class="btn-cancel" @click="goBack">取消</button>
      <button class="btn-submit" @click="submitQuote" :disabled="submitting">
        {{ submitting ? '提交中...' : '提交报价' }}
      </button>
    </view>
  </view>
</template>

<script>
import api from '../../api'
export default {
  data() {
    return {
      orderId: null, orderNo: '', serviceFee: 0, materialFee: 0,
      quoteItems: [], submitting: false,
      serviceItems: [], searchKeyword: '', selectedServiceId: null,
      showSelector: false,
    }
  },
  computed: {
    totalAmount() {
      return this.quoteItems.reduce((s, i) => s + (Number(i.quantity)||1) * (Number(i.unit_price)||0), 0)
        + Number(this.serviceFee) + Number(this.materialFee)
    },
    filteredItems() {
      const kw = this.searchKeyword.trim().toLowerCase()
      if (!kw) return this.serviceItems
      return this.serviceItems.filter(i => i.name.toLowerCase().includes(kw))
    }
  },
  onLoad(q) {
    this.orderId = q.id; this.orderNo = q.no || ''
    if (q.parts) {
      this.quoteItems.push({ name: '检测费', quantity: 1, unit_price: 30 })
    }
    this.loadServiceItems()
  },
  methods: {
    async loadServiceItems() {
      try {
        const res = await api.getServiceItems()
        this.serviceItems = (Array.isArray(res.data) ? res.data : res.data?.items || [])
          .filter(i => i.level >= 2) // 只显示二级及以下的具体项目
      } catch(e) {
        // 加载失败时使用默认预设
        this.serviceItems = []
      }
    },
    selectService(item) {
      this.selectedServiceId = item.id
      // 检查是否已添加
      const existing = this.quoteItems.find(i => i.service_item_id === item.id)
      if (existing) {
        existing.quantity++
        this.selectedServiceId = null
        return
      }
      this.quoteItems.push({
        service_item_id: item.id,
        name: item.name,
        quantity: 1,
        unit_price: item.default_price || 0,
      })
      this.selectedServiceId = null
      this.searchKeyword = ''
    },
    showServiceSelector() {
      if (!this.serviceItems.length) {
        this.addCustomItem()
        return
      }
      // 用ActionSheet显示常用项目
      const list = this.serviceItems.slice(0, 15).map(i =>
        i.name + (i.default_price ? ' ¥' + i.default_price : '')
      )
      list.push('✏️ 手动输入')
      uni.showActionSheet({
        itemList: list,
        success: (r) => {
          if (r.tapIndex < this.serviceItems.length && r.tapIndex < 15) {
            this.selectService(this.serviceItems[r.tapIndex])
          } else {
            this.addCustomItem()
          }
        }
      })
    },
    addCustomItem() {
      this.quoteItems.push({ name: '', quantity: 1, unit_price: 0 })
      // 自动聚焦到新项目的名称输入
    },
    removeItem(i) {
      if (this.quoteItems.length <= 1) { uni.showToast({ title:'至少保留一个项目', icon:'none' }); return }
      uni.showModal({ title:'提示', content:`删除「${this.quoteItems[i].name||'未命名'}」？`, success: (r) => { if (r.confirm) this.quoteItems.splice(i, 1) } })
    },
    goBack() { uni.navigateBack() },
    async submitQuote() {
      const validItems = this.quoteItems.filter(i => i.name && i.name.trim())
      if (!validItems.length) { uni.showToast({ title:'请至少添加一个项目', icon:'none' }); return }
      if (this.totalAmount <= 0) { uni.showToast({ title:'请输入有效金额', icon:'none' }); return }
      this.submitting = true
      try {
        await api.submitQuote(this.orderId, {
          items: validItems,
          total_amount: this.totalAmount,
          service_fee: Number(this.serviceFee),
          material_fee: Number(this.materialFee),
          remark: ''
        })
        uni.showToast({ title: '报价已提交' })
        uni.navigateBack()
      } catch(e) { uni.showToast({ title: e.message || '提交失败', icon:'none' }) }
      finally { this.submitting = false }
    }
  }
}
</script>

<style>
.page{background:var(--bg-page);min-height:100vh;padding-bottom:80px;width:100%;overflow-x:hidden;box-sizing:border-box}
.header-bar{display:flex;align-items:center;justify-content:space-between;padding:var(--spacing-md);background:var(--bg-card);border-bottom:1px solid var(--border);position:sticky;top:0;z-index:10}
.back-btn{font-size:var(--font-md);color:var(--primary);font-weight:500}
.title-txt{font-size:var(--font-lg);font-weight:600;color:var(--text-primary)}
.order-ref{font-size:var(--font-sm);color:var(--text-tertiary);padding:8px 16px 0}

/* 选择服务项目 */
.section{background:var(--bg-card);border-radius:var(--radius-md);margin:var(--spacing-sm) var(--spacing-md);padding:var(--spacing-lg);box-shadow:var(--shadow-sm);border:1px solid var(--border)}
.sec-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:var(--spacing-md)}
.sec-title{font-size:var(--font-lg);font-weight:600;color:var(--text-primary)}
.sec-hint{font-size:var(--font-sm);color:var(--text-tertiary)}
.sec-count{font-size:var(--font-sm);color:var(--primary);background:var(--primary-light);padding:2px 10px;border-radius:var(--radius-sm);font-weight:500}

.service-selector{border:1.5px solid var(--border);border-radius:var(--radius-sm);overflow:hidden;margin-bottom:var(--spacing-sm);max-height:220px}
.ss-search{display:flex;align-items:center;gap:6px;padding:8px 10px;background:var(--bg-fill);border-bottom:1px solid var(--border)}
.ss-search-icon{font-size:var(--font-md)}
.ss-search-input{flex:1;border:none;background:none;font-size:var(--font-base);padding:4px 0;outline:none}
.ss-list{max-height:168px;overflow-y:auto}
.ss-item{display:flex;justify-content:space-between;align-items:center;padding:10px 12px;border-bottom:1px solid #f0f0f0;transition:background .1s}
.ss-item:active{background:var(--primary-light)}
.ss-item.ss-active{background:var(--primary-light)}
.ss-item-name{font-size:var(--font-base);font-weight:500;color:var(--text-primary)}
.ss-item-unit{font-size:var(--font-sm);color:var(--text-tertiary);margin-left:6px}
.ss-item-price{font-size:var(--font-base);font-weight:600;color:var(--primary)}
.ss-item-add{color:var(--success);font-size:var(--font-lg);font-weight:700;margin-left:8px}
.add-custom-btn{width:100%;padding:8px;border:1px dashed var(--border-strong);border-radius:var(--radius-sm);background:none;color:var(--text-tertiary);font-size:var(--font-sm)}

.quote-card{background:var(--bg-fill);border-radius:var(--radius-sm);padding:var(--spacing-md);margin-bottom:var(--spacing-sm);border:1px solid var(--border)}
.qc-top{display:flex;align-items:center;gap:var(--spacing-sm);margin-bottom:var(--spacing-sm)}
.qc-num{width:22px;height:22px;border-radius:50%;background:var(--primary-gradient);color:#fff;text-align:center;line-height:22px;font-size:var(--font-sm);font-weight:600;flex-shrink:0}
.qc-name{flex:1;padding:8px 10px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-size:var(--font-base);background:var(--bg-card);outline:none;transition:border-color .2s}
.qc-name:focus{border-color:var(--primary)}
.qc-del{padding:4px 6px;color:var(--text-tertiary);font-size:var(--font-lg)}
.qc-detail{display:flex;align-items:center;gap:var(--spacing-sm)}
.qc-field{display:flex;align-items:center;gap:4px;background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius-sm);padding:4px 8px}
.qc-label{font-size:var(--font-sm);color:var(--text-tertiary);white-space:nowrap}
.qc-input{border:none;outline:none;font-size:var(--font-base);text-align:center;background:none;padding:4px 0}
.qc-input.qty{width:40px}
.qc-input.price{width:60px}
.qc-subtotal{margin-left:auto;text-align:right}
.qc-st-label{font-size:var(--font-sm);color:var(--text-tertiary);display:block}
.qc-st-val{font-size:var(--font-md);font-weight:600;color:var(--primary)}

.add-btn{width:100%;padding:var(--spacing-sm);border:1.5px dashed var(--border-strong);border-radius:var(--radius-sm);background:none;color:var(--primary);font-size:var(--font-base);margin-top:var(--spacing-xs)}

.fee-row{display:flex;align-items:center;justify-content:space-between;padding:var(--spacing-sm) 0;border-bottom:1px solid var(--border)}
.fee-row:last-child{border-bottom:none}
.fee-label{font-size:var(--font-base);color:var(--text-secondary)}
.fee-input-wrap{display:flex;align-items:center;gap:4px}
.fee-input{width:80px;padding:8px 10px;border:1.5px solid var(--border);border-radius:var(--radius-sm);font-size:var(--font-md);text-align:right;background:var(--bg-fill);outline:none;transition:border-color .2s}
.fee-input:focus{border-color:var(--primary)}
.fee-unit{font-size:var(--font-sm);color:var(--text-tertiary)}

.total-card{background:var(--primary-gradient);border-radius:var(--radius-lg);margin:var(--spacing-sm) var(--spacing-md);padding:20px;display:flex;justify-content:space-between;align-items:center;box-shadow:0 4px 12px rgba(230,122,46,.2)}
.total-left{flex:1}
.total-label{font-size:var(--font-md);color:rgba(255,255,255,.7)}
.total-hint{font-size:var(--font-sm);color:rgba(255,255,255,.4);margin-top:2px;display:block}
.total-amount{font-size:32px;font-weight:700;color:#fff}

.bottom-bar{position:fixed;bottom:0;left:0;right:0;display:flex;gap:var(--spacing-sm);padding:var(--spacing-md) var(--spacing-md) calc(var(--spacing-md) + env(safe-area-inset-bottom,0px));background:var(--bg-card);border-top:1px solid var(--border);box-shadow:0 -2px 10px rgba(0,0,0,.05)}
.btn-cancel{flex:1;padding:14px;border:none;border-radius:var(--radius-sm);background:var(--bg-fill);font-size:var(--font-lg);font-weight:600;color:var(--text-secondary)}
.btn-submit{flex:2;padding:14px;border:none;border-radius:var(--radius-sm);background:var(--primary-gradient);font-size:var(--font-lg);font-weight:600;color:#fff;transition:opacity .2s}
.btn-submit:active{opacity:.85}
.btn-submit[disabled]{opacity:.5}
</style>
