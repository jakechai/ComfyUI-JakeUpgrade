@echo off

echo Installing ComfyUI's JakeUpgrade Nodes with ComfyUI Portable..

REM python path
set "python_exec="E:\Program Files\ComfyUI_windows_portable\python_embeded\python.exe""

%python_exec% -s -m pip install opencv-python
%python_exec% -s -m pip install piexif
%python_exec% -s -m pip install torch
%python_exec% -s -m pip install numpy<2
%python_exec% -s -m pip install numexpr
%python_exec% -s -m pip install simpleeval

pause