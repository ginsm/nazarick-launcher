python -m PyInstaller^
 --clean^
 --noconfirm^
 --icon=nazaricklauncher.ico^
 --distpath temp/dist^
 --workpath temp/build^
 --add-data %UserProfile%\AppData\Roaming\Python\Python312\site-packages\customtkinter:customkinter\^
 --add-data temp/repository/metadata/root.json:.^
 --add-data F:\Projects\Active\nazarick-launcher\src\icons:icons\^
 --add-data F:\Projects\Active\nazarick-launcher\src\themes:themes\^
 --add-binary "nazaricklauncher.ico;."^
 --onedir^
 --windowed^
 --noconsole^
 --name "Nazarick Launcher"^
 F:\Projects\Active\nazarick-launcher\src\app.py

pause
