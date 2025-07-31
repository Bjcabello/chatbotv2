@echo off
call venv\Scripts\activate
uvicorn src.main:app --reload
pause