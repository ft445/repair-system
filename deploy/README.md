# 云匠 - 腾讯云部署指南

## 第一步：购买服务器
腾讯云 → 轻量应用服务器 → Ubuntu 22.04 → 2核2G即可

## 第二步：上传代码到服务器
```bash
# 在你电脑上（Windows PowerShell / CMD）:
scp -r C:\Users\Administrator\Desktop\repair-system root@你的服务器IP:/root/
```

## 第三步：SSH登录服务器执行部署
```bash
ssh root@你的服务器IP
cd /root/repair-system/deploy
bash deploy.sh 你的域名.com
```

## 第四步：配置微信服务号

### 1. 申请服务号
- 前往 https://mp.weixin.qq.com
- 注册 → 选择服务号
- 需要：邮箱、营业执照（或个人身份证）

### 2. 配置公众号
| 设置 | 说明 |
|------|------|
| 网页授权域名 | 填写你的域名 |
| JS接口安全域名 | 填写你的域名 |
| IP白名单 | 添加服务器IP |

### 3. 创建菜单
登录公众号后台 → 菜单管理 → 添加菜单：

```
📋 报修服务        👤 我的        💬 帮助
├─ 在线报修        ├─ 工单查询    ├─ AI客服
├─ 服务价格表      └─ 个人中心    └─ 常见问题
```

### 4. 公众号自动回复
```
被关注回复: 欢迎来到云匠！点击「在线报修」一键下单
关键词回复: "价格" → 弹出价格表
             "客服" → 转接AI客服
```

## 第五步：师傅端APP打包
用 HBuilderX 打开 technician-app 目录 → 发行 → 云打包
