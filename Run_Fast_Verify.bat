@echo off
chcp 65001 >nul
title Kipas Fast Verification Solver
cd /d "%~dp0"
echo ========================================================
echo        KIPAS FOOTBALL - FAST VERIFICATION SOLVER       
echo ========================================================
echo.
set /p verify_url="ضع رابط التحقق هنا (Paste Link): "
echo.
echo [*] جاري تشغيل المحرك السريع وتنفيذ التحقق فوراً...
python kipas_fast_solver.py "%verify_url%"
echo.
echo ========================================================
pause
