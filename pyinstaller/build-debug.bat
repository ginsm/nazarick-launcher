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
 --console^
 --name "Nazarick Launcher (Debug)"^
 F:\Projects\Active\nazarick-launcher\src\app.py

pause
