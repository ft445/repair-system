#!/bin/bash
# 黄师傅维修 APK 构建脚本
# 用法: ./build-apk.sh

export JAVA_HOME="/c/Program Files/Eclipse Adoptium/jdk-17.0.19.10-hotspot"
export ANDROID_HOME="$(cd "$(dirname "$0")" && pwd)/android-sdk"
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/platform-tools:$ANDROID_HOME/latest/bin:$PATH"

cd "$(dirname "$0")"

echo "=== 1. 构建 H5 ==="
npx vite build --emptyOutDir false

echo "=== 2. 同步到 Android ==="
npx cap copy
npx cap sync

echo "=== 3. 打包 APK ==="
cd android
./gradlew assembleDebug

echo "=== 完成 ==="
ls -la app/build/outputs/apk/debug/*.apk
