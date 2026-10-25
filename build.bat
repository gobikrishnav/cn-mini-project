@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo   Building NetLab-Pro: IPv4 Subnet Suite in C
echo ============================================================

if not exist "bin" mkdir "bin"
if not exist "reports" mkdir "reports"

:: Check if GCC is available
where gcc >nul 2>nul
if !ERRORLEVEL! equ 0 (
    echo [INFO] Compiling Terminal Edition with GCC...
    gcc -std=c99 -Wall -Wextra -Iinclude src/main.c src/ip_calc.c src/vlsm_engine.c src/flsm_engine.c src/host_inventory.c src/reachability.c src/cisco_export.c src/quiz_engine.c src/ui_framework.c -o bin/netlab.exe
    
    echo [INFO] Compiling GUI Desktop Edition with GCC...
    gcc -std=c99 -Wall -Wextra -Iinclude src/gui_main.c src/ip_calc.c src/vlsm_engine.c src/cisco_export.c src/reachability.c -o bin/netlab_gui.exe -mwindows -lcomctl32 -lgdi32 -luser32
    
    goto verify
)

:: Check for MSVC vcvars64.bat in Visual Studio 2022 BuildTools
set "VCVARS=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
if exist "%VCVARS%" (
    echo [INFO] Initializing Microsoft MSVC environment...
    call "%VCVARS%" >nul 2>nul

    echo [INFO] Compiling C Native Core Backend [netlab_core.dll]...
    cl.exe /nologo /LD /W3 /D_CRT_SECURE_NO_WARNINGS /Iinclude /utf-8 /Febin\netlab_core.dll src\c_backend.c src\ip_calc.c src\vlsm_engine.c src\flsm_engine.c src\supernet_engine.c src\host_inventory.c src\reachability.c src\cisco_export.c >nul 2>nul

    echo [INFO] Compiling Terminal Edition [netlab.exe]...
    cl.exe /nologo /W3 /D_CRT_SECURE_NO_WARNINGS /Iinclude /utf-8 /Febin\netlab.exe src\main.c src\ip_calc.c src\vlsm_engine.c src\flsm_engine.c src\host_inventory.c src\reachability.c src\cisco_export.c src\quiz_engine.c src\ui_framework.c >nul 2>nul
    
    echo [INFO] Compiling Windows Desktop GUI Edition [netlab_gui.exe]...
    cl.exe /nologo /W3 /D_CRT_SECURE_NO_WARNINGS /Iinclude /utf-8 /Febin\netlab_gui.exe src\gui_main.c src\ip_calc.c src\vlsm_engine.c src\cisco_export.c src\reachability.c user32.lib gdi32.lib comctl32.lib shell32.lib >nul 2>nul
    
    del *.obj 2>nul
    del bin\*.exp 2>nul
    goto verify
)

echo [ERROR] C compiler not found.
goto fail

:verify
if exist "bin\netlab.exe" if exist "bin\netlab_gui.exe" if exist "bin\netlab_core.dll" (
    echo.
    echo [SUCCESS] All C targets compiled successfully!
    echo   1. bin\netlab_core.dll [C Native Core Backend Engine DLL]
    echo   2. bin\netlab.exe      [Terminal / TUI Edition]
    echo   3. bin\netlab_gui.exe  [Native Windows Desktop GUI Edition]
    goto done
) else (
    echo [ERROR] Build failed.
    goto fail
)

:done
echo.
echo ============================================================
echo   Quick Launchers:
echo     * run_gui.bat  - Launch Native Windows Desktop GUI
echo     * run.bat      - Launch Interactive Terminal TUI
echo ============================================================
exit /b 0

:fail
echo.
echo [FAILED] Compilation failed.
exit /b 1
