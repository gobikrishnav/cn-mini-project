@echo off
setlocal
echo ========================================================
echo   NetLab-Pro :: Push to GitHub for Render Deployment
echo ========================================================
echo.
set /p REPO_URL="Enter your GitHub Repository URL (e.g., https://github.com/gobikrishnav/cn-mini-project.git): "

if "%REPO_URL%"=="" (
    echo [ERROR] No URL entered.
    pause
    exit /b 1
)

git remote remove origin 2>nul
git remote add origin %REPO_URL%
git branch -M main

echo.
echo Pushing to GitHub...
git push -u origin main

if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================================
    echo   [SUCCESS] Code pushed to GitHub!
    echo   Now on Render (https://dashboard.render.com):
    echo   1. Click 'New +' -> 'Web Service'
    echo   2. Select your repository
    echo   3. Render will auto-detect 'render.yaml' and deploy!
    echo ========================================================
) else (
    echo.
    echo [ERROR] Push failed. Make sure the repository exists and you are authenticated.
)

pause
