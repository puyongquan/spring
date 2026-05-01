@echo off
chcp 65001 >nul

echo ================================
echo        克隆 GitHub 仓库
echo ================================
echo.

set /p url=请输入仓库地址（右键粘贴）: 

echo.
echo 正在克隆...
git clone %url%

echo.
echo ================================
echo           完成！
echo ================================
pause