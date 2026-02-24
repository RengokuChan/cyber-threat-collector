Set WshShell = CreateObject("WScript.Shell")
' Le 0 à la fin permet de lancer le script de façon totalement invisible
WshShell.Run "pythonw.exe bot_discord.py", 0
Set WshShell = Nothing