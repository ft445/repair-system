<template>
  <view class="page">
    <view class="form-section">
      <view class="form-row">
        <text class="form-label">姓名</text>
        <input class="form-input" v-model="form.name" placeholder="请输入姓名" />
      </view>
      <view class="form-row">
        <text class="form-label">手机号</text>
        <input class="form-input" v-model="form.phone" placeholder="请输入手机号" type="number" maxlength="11" />
      </view>
      <view class="form-row">
        <text class="form-label">住址</text>
        <input class="form-input" v-model="form.address" placeholder="请输入住址" />
      </view>
      <view class="form-row">
        <text class="form-label">身份证</text>
        <input class="form-input" v-model="form.id_card" placeholder="请输入身份证号" disabled style="color:#999" />
      </view>
      <view class="form-row">
        <text class="form-label">紧急联系人</text>
        <input class="form-input" v-model="form.emergency_contact" placeholder="请输入紧急联系人姓名" />
      </view>
      <view class="form-row">
        <text class="form-label">紧急电话</text>
        <input class="form-input" v-model="form.emergency_phone" placeholder="请输入紧急联系电话" type="number" />
      </view>
    </view>

    <button class="save-btn" @click="saveProfile">保存修改</button>
  </view>
</template>

<script>
import api from '../../api'
export default {
  data() {
    return {
      user: null,
      form: { name: '', phone: '', address: '', id_card: '', emergency_contact: '', emergency_phone: '' }
    }
  },
  onLoad() {
    this.user = uni.getStorageSync('user')
    if (!this.user) return uni.reLaunch({ url: '/pages/login/index' })
    this.loadProfile()
  },
  methods: {
    async loadProfile() {
      try {
        const res = await api.getMyInfo(this.user.id)
        const d = res.data || {}
        this.form.name = d.name || this.user.name || ''
        this.form.phone = d.phone || ''
        this.form.address = d.address || ''
        this.form.id_card = d.id_card || ''
        this.form.emergency_contact = d.emergency_contact || ''
        this.form.emergency_phone = d.emergency_phone || ''
      } catch(e) {
        // fallback to cached user
        this.form.name = this.user.name || ''
        this.form.phone = this.user.phone || ''
      }
    },
    async saveProfile() {
      if (!this.form.name) { uni.showToast({ title: '请输入姓名', icon: 'none' }); return }
      try {
        await api.updateProfile(this.user.id, {
          name: this.form.name,
          phone: this.form.phone,
          address: this.form.address,
          emergency_contact: this.form.emergency_contact,
          emergency_phone: this.form.emergency_phone,
        })
        // 更新本地缓存
        const cached = uni.getStorageSync('user') || {}
        cached.name = this.form.name
        cached.phone = this.form.phone
        uni.setStorageSync('user', cached)
        uni.showToast({ title: '保存成功', icon: 'success' })
        setTimeout(() => uni.navigateBack(), 500)
      } catch(e) {
        uni.showToast({ title: e.message || '保存失败', icon: 'none' })
      }
    }
  }
}
</script>

<style>
.page{background:var(--bg-page);min-height:100vh;padding:var(--spacing-md)}
.form-section{background:var(--bg-card);border-radius:var(--radius-lg);padding:var(--spacing-lg);box-shadow:var(--shadow-sm);border:1px solid var(--border)}
.form-row{display:flex;align-items:center;padding:var(--spacing-md) 0;border-bottom:1px solid var(--border)}
.form-row:last-child{border-bottom:none}
.form-label{width:80px;font-size:var(--font-md);color:var(--text-secondary);flex-shrink:0;font-weight:500}
.form-input{flex:1;padding:var(--spacing-sm) var(--spacing-md);border:none;background:var(--bg-fill);border-radius:var(--radius-sm);font-size:var(--font-md);color:var(--text-primary)}
.save-btn{width:100%;margin-top:var(--spacing-xl);padding:14px;border:none;border-radius:var(--radius-md);background:var(--primary-gradient);color:#fff;font-size:17px;font-weight:600;text-align:center}
.save-btn:active{opacity:.85}
</style>
