@echo off

echo Installing ComfyUI's JakeUpgrade Nodes with ComfyUI Portable..

set "python_exec="../../../python_embeded/python.exe""

%python_exec% -s -m pip install -r requirements.txt

pause