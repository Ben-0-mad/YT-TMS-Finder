@echo off
set Location=C:%HOMEPATH%\AppData\Local\Programs\Python\

:Check to see if the Python directory exists, if not, display error message:
IF EXIST "%Location%" ( 
    python find_stable.py -m 3
) ELSE (
    echo This program uses Python, which is not installed on your system. Please download and install Python at https://www.python.org/downloads/. & pause
)