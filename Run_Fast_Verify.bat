@echo off
chcp 65001 >nul
title Kipas Fast Verification Solver
cd /d "%~dp0"
python kipas_fast_solver.py
pause
