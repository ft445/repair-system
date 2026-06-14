/**
 * 构建后处理脚本：将 uni-app H5 构建打包成单个 APK 可用格式
 *
 * uni-app H5 构建输出：
 *   assets/index-xxx.js  (4KB - 入口加载器)
 *   build/app/app-service.js  (141KB - 主应用代码)
 *   build/app/app-config-service.js (配置)
 *   build/app/uni-app-view.umd.js (视图框架)
 *   build/app/pages/*.css (页面样式)
 *   build/.nvue/app.js (NVue)
 *
 * 问题：入口 JS 通过动态 import() 加载这些文件，
 * 在 file:// 协议下动态 import 失败 → 页面空白。
 *
 * 修复：将所有 JS 合并成一个文件，CSS 也合并。
 */
const fs = require('fs')
const path = require('path')

const distDir = path.resolve(__dirname, '../dist')

// 1. 读取 index.html
let html = fs.readFileSync(path.join(distDir, 'index.html'), 'utf-8')

// 2. 收集所有 JS 文件（按加载顺序）
const jsFiles = [
  // 入口
  'assets/index-CE8RTygH.js',
  // 主应用
  'build/app/app-service.js',
  'build/app/app-config-service.js',
  'build/app/uni-app-view.umd.js',
  // uni-app 辅助模块
  'build/app/app-config.js',
  'build/.nvue/app.js',
  // 页面自动注册脚本
  'build/app/__uniappautomator.js',
  'build/app/__uniapppicker.js',
  'build/app/__uniappscan.js',
  'build/app/__uniappchooselocation.js',
  'build/app/__uniappopenlocation.js',
  'build/app/__uniappquill.js',
  'build/app/__uniappquillimageresize.js',
]

// 3. 合并所有 JS
let allJs = '// 黄师傅维修 - 合并构建\n'
let loadedCount = 0
for (const jsFile of jsFiles) {
  const filePath = path.join(distDir, jsFile)
  if (fs.existsSync(filePath)) {
    allJs += `\n// === ${jsFile} ===\n`
    allJs += fs.readFileSync(filePath, 'utf-8') + '\n'
    loadedCount++
    console.log(`  ✓ ${jsFile} (${(fs.statSync(filePath).size/1024).toFixed(0)}KB)`)
  } else {
    console.log(`  ✗ ${jsFile} - NOT FOUND`)
  }
}

// 4. 写合并后的 app.js
const jsOut = path.join(distDir, 'assets', 'app.js')
fs.writeFileSync(jsOut, allJs)
console.log(`\n📦 合并完成: ${loadedCount} 个文件 → assets/app.js (${(allJs.length/1024).toFixed(0)}KB)`)

// 5. 合并所有 CSS
let allCss = ''
const cssFiles = [
  'assets/index-DoJf7LIY.css',
  'build/app/app.css',
  'build/.nvue/app.css.js',
]
for (const cf of cssFiles) {
  const fp = path.join(distDir, cf)
  if (fs.existsSync(fp)) {
    const content = fs.readFileSync(fp, 'utf-8')
    allCss += content + '\n'
    console.log(`  ✓ ${cf}`)
  }
}
// 页面 CSS
const pagesDir = path.join(distDir, 'build', 'app', 'pages')
if (fs.existsSync(pagesDir)) {
  for (const pageDir of fs.readdirSync(pagesDir)) {
    const cssFile = path.join(pagesDir, pageDir, 'index.css')
    if (fs.existsSync(cssFile)) {
      allCss += fs.readFileSync(cssFile, 'utf-8') + '\n'
    }
  }
}

// 写合并后的 CSS
fs.writeFileSync(path.join(distDir, 'assets', 'app.css'), allCss)
console.log(`📦 CSS 合并: ${(allCss.length/1024).toFixed(0)}KB`)

// 6. 生成新的 index.html
html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>黄师傅维修 - 师傅端</title>
  <link rel="stylesheet" href="./assets/app.css">
</head>
<body>
  <div id="app"></div>
  <script src="./assets/app.js"></script>
</body>
</html>`

fs.writeFileSync(path.join(distDir, 'index.html'), html, 'utf-8')
console.log('✅ index.html generated - single script + single CSS')
