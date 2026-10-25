@echo off
title NetLab-Pro Campus Network Subnet Architect & Dynamic VLSM Suite
cd /d "%~dp0"
cls
echo ===============================================================================
echo            NetLab-Pro :: Campus Network Subnet Architect & VLSM Suite
echo             User-Driven Input Mode - Essential Project Edition
echo ===============================================================================
echo.
echo   [1] Launch Modern Web Application (Recommended: Chrome / Default Browser)
echo       - User Input Setup Wizard: Define Labs, Names, Systems, VLANs
echo       - 4-Tier Network Topology, Workstation Fleet, 32-Bit Binary Visualizer
echo       - L2/L3 Diagnostics, CIDR Supernetting, Viva Defense Quiz
echo.
echo   [2] Launch Native Desktop GUI Studio (Tkinter Windows Application)
echo.
echo   [3] Launch Interactive Terminal CLI Wizard
echo.
echo ===============================================================================
set /p choice="Select an option [1-3] (Default is 1): "
if "%choice%"=="" set choice=1
if "%choice%"=="1" goto web
if "%choice%"=="2" goto gui
if "%choice%"=="3" goto cli
echo Invalid option selected, launching Web Application...
goto web

:web
echo Starting NetLab-Pro Web Server & Opening Browser...
python server.py
pause
exit

:gui
echo Launching NetLab-Pro Native Desktop GUI Studio...
python gui_app.py
pause
exit

:cli
echo Launching NetLab-Pro Interactive CLI...
python interactive_cli.py
pause
exit
