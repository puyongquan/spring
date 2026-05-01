@echo off
chcp 65001 >nul
cd /d E:\实用小工具

echo ================================
echo        上传代码到 GitHub
echo ================================
echo.

set /p msg=请输入本次修改说明（直接回车默认"更新代码"）: 
if "%msg%"=="" set msg=更新代码

echo.
echo 正在添加文件...
git add .

echo 正在提交...
git commit -m "%msg%"

echo 正在推送到 GitHub...
git push

echo.
echo ================================
echo           完成！
echo ================================
pause