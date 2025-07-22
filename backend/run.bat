@echo off
call venv\Scripts\activate
python -m src.load_docs
uvicorn src.main:app --reload
pause