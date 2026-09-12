Set WshShell = CreateObject("WScript.Shell")
Set objWMIService = GetObject("winmgmts:\\.\root\cimv2")

Set colProcesses = objWMIService.ExecQuery("Select * from Win32_Process Where Name = 'pythonw.exe' OR Name = 'python.exe'")

bIsRunning = False
For Each objProcess in colProcesses
    If Not IsNull(objProcess.CommandLine) Then
        If InStr(1, objProcess.CommandLine, "main.py", 1) > 0 Or InStr(1, objProcess.CommandLine, "PlantComplainer", 1) > 0 Or InStr(1, objProcess.CommandLine, "PlantCompanion", 1) > 0 Then
            bIsRunning = True
            objProcess.Terminate()
        End If
    End If
Next

If bIsRunning Then
    WshShell.Popup "🌱 Plant Companion has been turned OFF.", 3, "Plant Companion", 64
Else
    WshShell.CurrentDirectory = "C:\Users\archa\Desktop\PlantComplainer_App"
    WshShell.Run """C:\Users\archa\AppData\Local\Programs\Python\Python313\pythonw.exe"" ""C:\Users\archa\Desktop\PlantComplainer_App\main.py""", 0, False
    WshShell.Popup "🌱 Plant Companion has been turned ON!", 3, "Plant Companion", 64
End If

