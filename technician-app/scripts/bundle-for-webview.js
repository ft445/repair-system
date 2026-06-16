/**
 * 构建后处理脚本：将 uni-app H5 构建打包成单个 APK 可用格式
 *
 * uni-app H5 构建使用动态 import() 加载多个 chunk，
 * 在 file:// 协议下动态 import 失败 → 页面空白。
 *
 * 修复：将所有 JS/CSS 合并成单个文件，按正确顺序加载。
 */
const fs = require('fs')
const path = require('path')

const distDir = path.resolve(__dirname, '../dist')
const html = fs.readFileSync(path.join(distDir, 'index.html'), 'utf-8')

// ======= 合并所有 JS（按依赖顺序） =======
const jsFiles = [
  // 1. uni-app 运行时（必须先加载，定义 uni 对象）
  'build/app/uni-app-view.umd.js',
  // 2. 配置
  'build/app/app-config-service.js',
  'build/app/app-config.js',
  // 3. 主应用（使用 uni.* API）
  'build/app/app-service.js',
  'build/.nvue/app.js',
  // 4. Vite 入口（最后加载）
  'assets/index-CE8RTygH.js',
  // 5. uni-app 辅助模块
  'build/app/__uniappautomator.js',
  'build/app/__uniapppicker.js',
  'build/app/__uniappscan.js',
  'build/app/__uniappchooselocation.js',
  'build/app/__uniappopenlocation.js',
  'build/app/__uniappquill.js',
  'build/app/__uniappquillimageresize.js',
]

let allJs = ''
let loadedCount = 0
for (const jsFile of jsFiles) {
  const filePath = path.join(distDir, jsFile)
  if (fs.existsSync(filePath)) {
    allJs += `\n// === ${jsFile} ===\n`
    allJs += fs.readFileSync(filePath, 'utf-8') + '\n'
    loadedCount++
    console.log(`  ✓ ${jsFile} (${(fs.statSync(filePath).size/1024).toFixed(0)}KB)`)
  } else {
    console.log(`  ✗ ${jsFile} NOT FOUND`)
  }
}

const jsOut = path.join(distDir, 'assets', 'app.js')
fs.writeFileSync(jsOut, allJs)
console.log(`\n📦 ${loadedCount} JS files → assets/app.js (${(allJs.length/1024).toFixed(0)}KB)`)

// ======= 合并所有 CSS =======
let allCss = ''
const cssFiles = [
  'assets/index-DoJf7LIY.css',
  'build/app/app.css',
]
for (const cf of cssFiles) {
  const fp = path.join(distDir, cf)
  if (fs.existsSync(fp)) {
    allCss += fs.readFileSync(fp, 'utf-8') + '\n'
  }
}
// 页面 CSS
const pagesDir = path.join(distDir, 'build', 'app', 'pages')
if (fs.existsSync(pagesDir)) {
  for (const pageDir of fs.readdirSync(pagesDir)) {
    const cssFile = path.join(pagesDir, pageDir, 'index.css')
    if (fs.existsSync(cssFile)) allCss += fs.readFileSync(cssFile, 'utf-8') + '\n'
  }
}
fs.writeFileSync(path.join(distDir, 'assets', 'app.css'), allCss)
console.log(`📦 CSS → assets/app.css (${(allCss.length/1024).toFixed(0)}KB)`)

// ======= 生成新的 index.html =======
const newHtml = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>云匠 - 师傅端</title>
  <link rel="stylesheet" href="./assets/app.css">
</head>
<body>
  <div id="app">加载中...</div>
  <script src="./assets/app.js"></script>
</body>
</html>`

fs.writeFileSync(path.join(distDir, 'index.html'), newHtml, 'utf-8')
console.log('✅ index.html generated')
