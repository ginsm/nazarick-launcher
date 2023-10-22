python -m PyInstaller^
 --noconfirm^
 --icon=nazaricklauncher.ico^
 --distpath temp/dist^
 --workpath temp/build^
 --add-data %UserProfile%\AppData\Roaming\Python\Python312\site-packages\customtkinter:customkinter\^
 --add-data temp/repository/metadata/root.json:.^
 --add-binary "nazaricklauncher.ico;."^
 --onedir^
 --windowed^
 --noconsole^
 --name "Nazarick Launcher"^
 F:\Projects\Active\nazarick-launcher\src\app.py

pause
