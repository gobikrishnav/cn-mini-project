@echo off
title Upload CN Mini Project to GitHub
cd /d "%~dp0"

echo ======================================================================
echo    NetLab-Pro :: Upload to GitHub (gobikrishnav) for Render
echo ======================================================================
echo.

:: Try using gh CLI
where gh >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [STEP 1] Logging into GitHub CLI...
    gh auth login -p https -w -h github.com
    
    echo.
    echo [STEP 2] Creating repository 'cn-mini-project' on your GitHub...
    gh repo create cn-mini-project --public --source=. --remote=origin --push
    goto check_result
)

:manual
echo.
echo Please create a repository on https://github.com/new named 'cn-mini-project'
set /p REPO_URL="Then paste the GitHub URL here (e.g. https://github.com/gobikrishnav/cn-mini-project.git): "
git remote remove origin 2>nul
git remote add origin %REPO_URL%
git branch -M main
git push -u origin main

:check_result
if %ERRORLEVEL% equ 0 (
    echo.
    echo ======================================================================
    echo   [SUCCESS] Your project is uploaded to GitHub!
    echo   Repository: https://github.com/gobikrishnav/cn-mini-project
    echo.
    echo   Now go to Render: https://dashboard.render.com
    echo   Click 'New +' -> 'Web Service' -> Select 'cn-mini-project'
    echo ======================================================================
) else (
    echo.
    echo [NOTE] If needed, you can push manually with your personal access token.
)

pause
