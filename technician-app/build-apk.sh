#!/bin/bash
# 云匠 APK 构建脚本 (标准 Vue 3 + Capacitor)
# 用法: ./build-apk.sh

export JAVA_HOME="/c/Program Files/Eclipse Adoptium/jdk-21.0.11.10-hotspot"
export ANDROID_HOME="$(cd "$(dirname "$0")" && pwd)/android-sdk"
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/platform-tools:$ANDROID_HOME/latest/bin:$PATH"

cd "$(dirname "$0")"

echo "=== 1. 清理旧构建 ==="
rm -rf dist

echo "=== 2. 构建 Vue 3 应用 ==="
./node_modules/.bin/vite build

echo "=== 2.5 注入 plus 垫片（Capacitor 兼容） ==="
node scripts/inject-plus-shim.js

echo "=== 3. 同步到 Android ==="
npx cap copy
npx cap sync

echo "=== 4. 打包 APK ==="
cd android
./gradlew assembleDebug

echo "=== 完成 ==="
ls -la app/build/outputs/apk/debug/*.apk
