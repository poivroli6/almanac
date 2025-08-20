@echo off
REM — switch to the script’s directory
cd /d "%~dp0"

REM — activate the venv
call .venv13\Scripts\activate.bat

REM — run the Almanac app
python Almanac_main.py