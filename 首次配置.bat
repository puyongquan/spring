@echo off
chcp 65001 >nul

echo 请输入你的 GitHub 用户名:
set /p name=
echo 请输入你的 GitHub 邮箱:
set /p email=

git config --global user.name "%name%"
git config --global user.email "%email%"

echo 配置完成！
pause