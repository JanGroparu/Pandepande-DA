Set WshShell = CreateObject("WScript.Shell")
Set oFSO     = CreateObject("Scripting.FileSystemObject")

' Run the icon setter from the subfolder
strIconVBS = oFSO.GetParentFolderName(WScript.ScriptFullName) & "\icon\set_ink_ico.vbs"
WshShell.Run "wscript //nologo """ & strIconVBS & """", 0, True

' Then launch the program
WshShell.Run "cmd /c venv\Scripts\Activate.bat & venv\Scripts\python.exe Visual.py", 0

Set WshShell = Nothing
Set oFSO     = Nothing