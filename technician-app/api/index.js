const API_BASE = (typeof process !== 'undefined' && process.env?.VITE_API_BASE) || 'https://zpqy.cn/api'

function request(path, options = {}) {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token')
    const header = {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
      ...options.header
    }
    uni.request({
      url: API_BASE + path,
      method: options.method || 'GET',
      data: options.data,
      header,
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data)
        } else if (res.statusCode === 401) {
          // 登录接口返回401 = 密码错误，其他接口 = token过期
          if (path === '/auth/login') {
            reject(new Error(res.data?.detail || '手机号或密码错误'))
          } else {
            uni.removeStorageSync('token')
            uni.reLaunch({ url: '/pages/login/index' })
            reject(new Error('登录已过期'))
          }
        } else {
          reject(new Error(res.data?.detail || '请求失败'))
        }
      },
      fail: (err) => reject(new Error('网络错误'))
    })
  })
}

export const api = {
  login(phone, password) {
    return request('/auth/login', { method: 'POST', data: { phone, password } })
  },
  getMyOrders(technicianId, status) {
    let path = `/technician/orders?technician_id=${technicianId}`
    if (status) path += `&status=${status}`
    return request(path)
  },
  getOrderDetail(orderId) { return request(`/orders/${orderId}`) },
  acceptOrder(orderId, technicianId) {
    return request(`/technician/orders/${orderId}/accept?technician_id=${technicianId}`, { method: 'POST' })
  },
  startService(orderId, technicianId) {
    return request(`/technician/orders/${orderId}/start`, { method: 'POST', data: { technician_id: technicianId } })
  },
  completeOrder(orderId, params) {
    const user = uni.getStorageSync('user')
    const data = { ...params, technician_id: user?.id }
    return request(`/technician/orders/${orderId}/complete`, { method: 'POST', data })
  },
  getServiceItems() { return request('/services/items') },
  getNearbyOrders(technicianId) { let path = '/technician/nearby'; if(technicianId) path += '?technician_id='+technicianId; return request(path) },
  getParts(orderId) { return request(`/orders/${orderId}/parts`) },
  addPart(orderId, data) { return request(`/orders/${orderId}/parts`, { method: 'POST', data }) },
  deletePart(partId) { return request(`/orders/parts/${partId}`, { method: 'DELETE' }) },
  submitQuote(orderId, data) { return request(`/orders/${orderId}/quote`, { method: 'POST', data }) },
  getQuote(orderId) { return request(`/orders/${orderId}/quote`) },
  chargeTripFee(orderId, data) { return request(`/orders/${orderId}/trip-fee`, { method: 'POST', data }) },
  markPaid(orderId, data) { return request(`/technician/orders/${orderId}/mark-paid`, { method: 'POST', data }) },
  clockIn(userId, address) { return request('/attendance/clock-in', { method: 'POST', data: { user_id: userId, address: address||'' } }) },
  clockOut(userId) { return request('/attendance/clock-out', { method: 'POST', data: { user_id: userId } }) },
  changePassword(oldPwd, newPwd) { return request('/auth/change-password', { method:'POST', data:{ old_password:oldPwd, new_password:newPwd } }) },
  rejectOrder(orderId, reason) { return request(`/technician/orders/${orderId}/reject`, { method:'POST', data:{ reason:reason||'师傅拒单' } }) },
  verifyCustomer(orderId, phoneTail) { return request(`/technician/orders/${orderId}/verify-customer`, { method:'POST', data:{ phone_tail:phoneTail } }) },
  rateOrder(orderId, rating, comment) { return request(`/technician/orders/${orderId}/rate`, { method:'POST', data:{ rating:rating, comment:comment||'' } }) },
  getSkills(techId) { return request(`/technician/${techId}/skills`) },
  updateLocation(latitude, longitude, userId) {
    return request('/attendance/location', { method: 'POST', data: { latitude, longitude, user_id: userId } })
  },
  createWithdraw(data) {
    return request('/finance/withdrawals', { method: 'POST', data })
  },
  getMyWithdrawals(userId) {
    return request(`/finance/withdrawals?user_id=${userId}`)
  },
  respondQuote(orderId, action) {
    return request(`/orders/${orderId}/quote/respond`, { method: 'POST', data: { action } })
  },
  getMyStats(technicianId) {
    return request(`/technician/list?filter=${technicianId}`)
  },
  getTechList() {
    return request('/technician/list')
  },
  transferOrder(orderId, data) {
    return request(`/orders/${orderId}/transfer`, { method: 'POST', data })
  },
  getDeposit(techId) { return request(`/technician/deposit/${techId}`) },
  payDeposit(techId, data) { return request(`/technician/deposit/${techId}`, { method: 'POST', data }) },
  getUnreadCount() { return request('/notifications/unread-count') },
  getNotifications(page, pageSize) { return request(`/notifications?page=${page}&page_size=${pageSize}`) },
  markNotificationRead(id) { return request(`/notifications/${id}`, { method: 'PUT', data: { is_read: true } }) },
  markAllRead() { return request('/notifications/read-all', { method: 'PUT' }) },
  getPublicSettings() { return request('/settings/public') },
  getMyOrdersPaginated(techId, { page=1, pageSize=20, status='' }={}) {
    let path = `/technician/orders?technician_id=${techId}&page=${page}&page_size=${pageSize}`
    if (status) path += `&status=${status}`
    return request(path)
  },
  getCustomerHistory(customerId, techId) { return request(`/orders?customer_id=${customerId}&technician_id=${techId}&page_size=20`) },
  getSchedule(techId, dateFrom, dateTo) { return request(`/technician/orders?technician_id=${techId}&date_from=${dateFrom}&date_to=${dateTo}&page_size=100`) },
  getMonthlyStats(techId) { return request(`/technician/stats/monthly?technician_id=${techId}`) },
  getMyInfo(userId) { return request(`/users/${userId}/profile`) },
  updateProfile(userId, data) { return request(`/users/${userId}/profile`, { method: 'PUT', data }) },
  getAttendanceToday(userId) { return request(`/attendance/today?user_id=${userId}`) },
  getMyLeaves(userId) { return request(`/attendance/leaves?user_id=${userId}`) },
  getMyRatings(techId) {
    return request(`/technician/orders?technician_id=${techId}&page_size=200`)
  }
}

export default api
