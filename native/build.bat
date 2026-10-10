@echo off
rem ===========================================================================
rem MyWalt Native Engine Build Script (Windows)
rem Compiles native_engine.cpp using MSVC (cl.exe) or GCC (g++)
rem ===========================================================================

setlocal
cd /d "%~dp0"

echo [*] Searching for C++ compiler...

rem 1. Check for MSVC (cl.exe)
where cl.exe >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [+] Compiling with Microsoft Visual C++ (MSVC)...
    cl /O2 /std:c++17 /EHsc native_engine.cpp /Fe:native_engine.exe
    if %ERRORLEVEL% equ 0 (
        echo [OK] native_engine.exe successfully compiled!
        del *.obj 2>nul
        exit /b 0
    )
)

rem 2. Check for GCC / MinGW (g++.exe)
where g++.exe >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [+] Compiling with MinGW GCC (g++)...
    g++ -O3 -std=c++17 native_engine.cpp -o native_engine.exe -static -lstdc++fs
    if %ERRORLEVEL% equ 0 (
        echo [OK] native_engine.exe successfully compiled!
        exit /b 0
    )
)

rem 3. Check for Clang (clang++)
where clang++.exe >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [+] Compiling with Clang (clang++)...
    clang++ -O3 -std=c++17 native_engine.cpp -o native_engine.exe
    if %ERRORLEVEL% equ 0 (
        echo [OK] native_engine.exe successfully compiled!
        exit /b 0
    )
)

echo [!] Notice: No active C++ compiler found in PATH or compiler was restricted.
echo [!] MyWalt backend will automatically run in high-compatibility Python fallback mode.
exit /b 1
