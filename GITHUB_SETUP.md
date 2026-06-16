# GitHub Actions 自动打包 APK 设置指南

## 1. 创建 GitHub 仓库

1. 打开 https://github.com/new
2. 仓库名：`repair-system`
3. 设为 **Public**（免费）或 **Private** 都可以
4. 不要勾选任何初始化选项
5. 点击 **Create repository**

## 2. 推送代码到 GitHub

打开终端（CMD 或 PowerShell），执行以下命令：

```bash
cd C:\Users\Administrator\Desktop\repair-system

# 添加 GitHub 仓库地址（替换 YOUR_USERNAME 为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/repair-system.git

# 添加所有文件
git add -A

# 提交
git commit -m "初始化：云匠系统 + 自动打包APK"

# 推送到 GitHub
git push -u origin main
```

> 如果提示登录，会弹出 GitHub 登录窗口，浏览器登录一次即可。

## 3. 触发自动打包

推送完成后：

1. 打开 https://github.com/YOUR_USERNAME/repair-system/actions
2. 会看到一个 **打包APK** 的工作流正在运行
3. 等待 3~5 分钟，构建完成后点击进入
4. 在 **Artifacts** 区域下载 APK 文件

### 手动触发

你也可以在 Actions 页面手动触发：

1. 点击 **打包APK** 工作流
2. 点击 **Run workflow** 按钮
3. 填写版本号（可选），点击 **Run**
4. 等待构建完成，下载 APK

## 4. 以后每次更新

每次修改 `technician-app/` 下的代码并推送到 `main` 分支时，GitHub Actions 会自动重新打包 APK。

下载的 APK 是 **Debug 版本**，可以直接安装到手机测试。如果需要正式发布（Release 版本 + 签名），后续可以配置签名证书。
