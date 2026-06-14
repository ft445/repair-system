/**
 * 构建后处理脚本：将 ES Module 打包成单个非 module 脚本
 * 解决 Android WebView 下 file:// 协议不执行 ES Module 的问题
 */
const fs = require('fs')
const path = require('path')

const distDir = path.resolve(__dirname, '../dist')

let html = fs.readFileSync(path.join(distDir, 'index.html'), 'utf-8')

// 找到所有 module script
const moduleScripts = []
const moduleRe = /<script type="module"[^>]*src="([^"]+)"[^>]*><\/script>/g
let m
while ((m = moduleRe.exec(html)) !== null) {
  moduleScripts.push(m[1])
}
console.log(`Found ${moduleScripts.length} module script(s)`)

// 读取并合并所有 JS
let allJs = ''
for (const src of moduleScripts) {
  const cleanSrc = src.replace(/^\.\//, '')
  const filePath = path.join(distDir, cleanSrc)
  if (fs.existsSync(filePath)) {
    allJs += fs.readFileSync(filePath, 'utf-8') + '\n'
    console.log(`  Bundled: ${cleanSrc}`)
  }
}

// 写合并后的 JS
const jsOut = path.join(distDir, 'assets', 'app.js')
fs.writeFileSync(jsOut, allJs)
console.log(`  Written: assets/app.js (${(allJs.length/1024).toFixed(0)}KB)`)

// 替换 HTML
html = html.replace(/<script type="module"[^>]*><\/script>/g, '')
html = html.replace('</head>', '  <script src="./assets/app.js"></script>\n</head>')
// 移除 duplicate link
html = html.replace(/<link rel="stylesheet"[^>]*>\n\s*<link rel="stylesheet"/g, '<link rel="stylesheet"')
// 移除 crossorigin（file:// 下不需要）
html = html.replace(/crossorigin /g, '')

fs.writeFileSync(path.join(distDir, 'index.html'), html, 'utf-8')
console.log('✅ index.html updated - module scripts converted to legacy')
