call C:\ProgramData\Anaconda3\Scripts\activate.bat C:\ProgramData\Anaconda3\
call conda activate BattleTechCC
del dist\BattleTechCC.exe
pyinstaller --onefile --name BattleTechCC "C:\Users\Anthony\Downloads\Tabletop\BattleTech\Character Creator\BattleTechCC\main.py"
del dist\BattleTechCC.zip
"C:\Program Files\7-Zip\7z.exe" a -mx=9 dist\BattleTechCC.zip .\dist\BattleTechCC.exe ..\resource\