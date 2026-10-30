@echo off
chcp 65001 >nul
title ChaiGPT Telegram Bot Runner
cd /d "%~dp0"
echo ========================================================
echo        ChaiGPT Telegram Bot - Running Locally           
echo ========================================================
echo.
echo [*] جاري تشغيل بوت التليجرام مع ميزة التحقق التلقائي...
python bot.py
echo.
pause
