<template>
  <view class="page">
    <view class="box">
      <text class="title">{{ brandName }}</text>
      <text class="sub">{{ brandSubtitle }}</text>
      <view class="card">
        <input class="inp" type="text" v-model="phone" placeholder="请输入手机号" maxlength="11" @tap="onTap"/>
        <input class="inp" type="password" v-model="password" placeholder="请输入密码" @tap="onTap"/>
        <button class="btn" @click="doLogin" :disabled="loading">{{ loading ? '登录中...' : '登 录' }}</button>
      </view>
    </view>
  </view>
</template>

<script>
import api from '../../api'
export default {
  data() { return { phone: '', password: '', loading: false, brandName: '云匠', brandSubtitle: '师傅端 · 接单平台' } },
  methods: {
    onTap(e) { if (e?.target?.focus) try { e.target.focus() } catch(e) {} },
    async doLogin() {
      if (!this.phone || !this.password) return uni.showToast({ title: '请输入手机号和密码', icon: 'none' })
      this.loading = true
      try {
        const res = await api.login(this.phone, this.password)
        const d = res.data
        uni.setStorageSync('token', d.access_token)
        uni.setStorageSync('user', d.user)
        uni.reLaunch({ url: '/pages/workbench/index' })
      } catch(e) { uni.showToast({ title: e.message, icon: 'none' }) }
      finally { this.loading = false }
    }
  }
}
</script>

<style>
.page{position:fixed;top:0;left:0;right:0;bottom:0;background:linear-gradient(180deg,#E67A2E,#C96A1F);display:flex;align-items:center;justify-content:center}
.box{width:88%;max-width:380px;display:flex;flex-direction:column;align-items:center}
.title{font-size:30px;font-weight:700;color:#fff;margin-bottom:4px;margin-top:-60px}
.sub{font-size:14px;color:rgba(255,255,255,.7);margin-bottom:30px}
.card{width:100%;background:#fff;border-radius:16px;padding:30px 24px 24px;box-shadow:0 8px 30px rgba(0,0,0,.1)}
.inp{width:100%;height:52px;padding:0 16px;border:1.5px solid #e8e8e8;border-radius:12px;font-size:17px;background:#f8f9fb;margin-bottom:16px;box-sizing:border-box;color:#333;outline:none}
.inp:focus{border-color:#E67A2E;background:#fff}
.btn{width:100%;height:52px;line-height:52px;padding:0;border:none;border-radius:12px;background:linear-gradient(135deg,#E67A2E,#C96A1F);color:#fff;font-size:18px;font-weight:600;margin-top:4px}
.btn[disabled]{opacity:.6}
</style>
