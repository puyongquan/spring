@echo off
chcp 65001 >nul
cd /d E:\实用小工具

echo ================================
echo      从 GitHub 拉取最新代码
echo ================================
echo.

echo 正在拉取...
git fetch --all
git reset --hard origin/main

echo.
echo ================================
echo           完成！
echo ================================
pause