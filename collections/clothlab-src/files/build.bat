@echo off
REM Build ClothLab with MinGW-w64 g++ (no third-party libraries required).
setlocal
cd /d "%~dp0"

if not exist bin mkdir bin

g++ -std=c++17 -O2 -Wall -static -static-libgcc -static-libstdc++ ^
    -o bin\ClothLab.exe ^
    src\main.cpp src\cloth.cpp src\renderer.cpp src\hud.cpp ^
    src\capture.cpp src\scene.cpp src\bench.cpp ^
    -lopengl32 -lgdi32 -luser32

if errorlevel 1 (
    echo.
    echo Build failed. Make sure g++ is in PATH.
    exit /b 1
)

echo.
echo Build OK: bin\ClothLab.exe
echo Run:  bin\ClothLab.exe
endlocal
