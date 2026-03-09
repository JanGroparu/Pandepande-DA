Set oShell = CreateObject("WScript.Shell")
Set oFSO   = CreateObject("Scripting.FileSystemObject")

' Folder containing the vbs and ico
strSelf   = oFSO.GetParentFolderName(WScript.ScriptFullName)
' One level up — where the shortcut is
strParent = oFSO.GetParentFolderName(strSelf)
strIcon   = strSelf & "\Pandepande.ico"

For Each oFile In oFSO.GetFolder(strParent).Files
    If LCase(oFSO.GetExtensionName(oFile.Name)) = "lnk" Then
        Set oLink = oShell.CreateShortcut(oFile.Path)
        oLink.IconLocation = strIcon & ", 0"
        oLink.Save
    End If
Next

Set oShell = Nothing
Set oFSO   = Nothing