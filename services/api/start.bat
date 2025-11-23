@echo off
cd /d "%~dp0..\.."
set PYTHONPATH=%CD%
cd services\api
python main.py
