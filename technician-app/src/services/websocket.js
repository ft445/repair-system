/**
 * WebSocket 连接服务
 * 师傅APP实时通知接收，兼容App(HBuilder)和H5环境
 */
const WS_BASE = (typeof process !== 'undefined' && process.env?.VITE_WS_BASE) || 'wss://zpqy.cn/api/ws'

class WsService {
  constructor() {
    this._ws = null
    this._userId = null
    this._token = null
    this._reconnectTimer = null
    this._reconnectAttempts = 0
    this._maxRetries = 10
    this._notifyCallbacks = []
    this._orderCallbacks = []
    this._connectedCallbacks = []
    this._disconnectedCallbacks = []
    this._heartbeatTimer = null
    this._manualDisconnect = false
    this._useUni = typeof uni !== 'undefined' && typeof uni.connectSocket !== 'undefined'
  }

  /** 建立连接 */
  connect(userId, token) {
    if (!userId || !token) return
    this._userId = userId
    this._token = token
    this._manualDisconnect = false
    this._reconnectAttempts = 0
    this._doConnect()
  }

  /** 断开连接 */
  disconnect() {
    this._manualDisconnect = true
    this._clearTimers()
    if (this._ws) {
      try {
        if (this._useUni && this._ws.close) {
          this._ws.close()
        } else if (this._ws.close) {
          this._ws.close(1000, '用户主动断开')
        }
      } catch (e) { /* ignore */ }
      this._ws = null
    }
  }

  /** 重新连接 */
  reconnect() {
    if (this._userId && this._token) {
      this._manualDisconnect = false
      this._reconnectAttempts = 0
      this._doConnect()
    }
  }

  /** 收到通知回调 */
  onNotification(callback) {
    if (typeof callback === 'function') this._notifyCallbacks.push(callback)
  }

  /** 工单状态变更回调 */
  onOrderUpdate(callback) {
    if (typeof callback === 'function') this._orderCallbacks.push(callback)
  }

  /** 连接成功回调 */
  onConnected(callback) {
    if (typeof callback === 'function') this._connectedCallbacks.push(callback)
  }

  /** 断开回调 */
  onDisconnected(callback) {
    if (typeof callback === 'function') this._disconnectedCallbacks.push(callback)
  }

  /** 获取连接状态 */
  isConnected() {
    return this._ws && (this._useUni ? true : this._ws.readyState === WebSocket.OPEN)
  }

  // ==================== 内部方法 ====================

  _doConnect() {
    if (!this._userId || !this._token) return
    this._clearTimers()

    const url = `${WS_BASE}/${this._userId}?token=${this._token}`

    if (this._useUni) {
      // uni-app H5/App 环境
      try {
        const socketTask = uni.connectSocket({ url, complete: () => {} })
        socketTask.onOpen(() => {
          this._ws = socketTask
          this._onOpen()
        })
        socketTask.onMessage((res) => this._onMessage(res.data))
        socketTask.onClose(() => this._onClose())
        socketTask.onError(() => this._onError())
      } catch (e) {
        this._scheduleReconnect()
      }
    } else {
      // 原生 WebSocket (H5 fallback)
      try {
        this._ws = new WebSocket(url)
        this._ws.onopen = () => this._onOpen()
        this._ws.onmessage = (e) => this._onMessage(e.data)
        this._ws.onclose = () => this._onClose()
        this._ws.onerror = () => this._onError()
      } catch (e) {
        this._scheduleReconnect()
      }
    }
  }

  _onOpen() {
    this._reconnectAttempts = 0
    this._startHeartbeat()
    this._connectedCallbacks.forEach(fn => { try { fn() } catch(e) {} })
  }

  _onMessage(data) {
    try {
      const msg = typeof data === 'string' ? JSON.parse(data) : data
      const type = msg.type || ''

      if (type === 'pong') {
        // 心跳回复，不做额外处理
        return
      }

      if (type === 'notification') {
        const notify = msg.data || msg
        // 触发通知回调
        this._notifyCallbacks.forEach(fn => { try { fn(notify) } catch(e) {} })
        // 如果是工单相关通知，也触发工单回调
        if (notify.type === 'order_dispatch' || notify.type === 'order_status') {
          this._orderCallbacks.forEach(fn => { try { fn(notify) } catch(e) {} })
        }
        return
      }

      if (type === 'connected') {
        // 连接成功确认
        return
      }
    } catch (e) {
      console.error('[WS] 消息解析失败:', e)
    }
  }

  _onClose() {
    this._ws = null
    this._clearTimers()
    this._disconnectedCallbacks.forEach(fn => { try { fn() } catch(e) {} })
    if (!this._manualDisconnect) {
      this._scheduleReconnect()
    }
  }

  _onError() {
    // onClose 会被连带触发，不需要重复处理
  }

  _scheduleReconnect() {
    if (this._manualDisconnect || this._reconnectAttempts >= this._maxRetries) return
    this._reconnectAttempts++
    // 指数退避：1s, 2s, 4s, 8s, 16s, 30s(上限)
    const delay = Math.min(1000 * Math.pow(2, this._reconnectAttempts - 1), 30000)
    this._reconnectTimer = setTimeout(() => {
      if (!this._manualDisconnect) this._doConnect()
    }, delay)
  }

  _startHeartbeat() {
    this._clearHeartbeat()
    this._heartbeatTimer = setInterval(() => {
      try {
        if (this._useUni && this._ws && this._ws.send) {
          this._ws.send({ data: JSON.stringify({ type: 'ping' }) })
        } else if (this._ws && this._ws.readyState === WebSocket.OPEN) {
          this._ws.send(JSON.stringify({ type: 'ping' }))
        }
      } catch (e) {
        // 连接可能已断开
      }
    }, 30000)
  }

  _clearHeartbeat() {
    if (this._heartbeatTimer) {
      clearInterval(this._heartbeatTimer)
      this._heartbeatTimer = null
    }
  }

  _clearTimers() {
    this._clearHeartbeat()
    if (this._reconnectTimer) {
      clearTimeout(this._reconnectTimer)
      this._reconnectTimer = null
    }
  }
}

// 全局单例
const wsService = new WsService()
export default wsService
