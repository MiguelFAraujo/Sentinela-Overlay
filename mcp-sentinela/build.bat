@echo off
echo Building Sentinela Hub...
uv run pyinstaller --onefile --name SentinelaHub server.py --clean
echo Build complete. Executable in dist/SentinelaHub.exe
pause
