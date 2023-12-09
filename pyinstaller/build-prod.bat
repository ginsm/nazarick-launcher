python -m PyInstaller^
 --clean^
 --noconfirm^
 --icon=nazaricklauncher.ico^
 --distpath temp/dist^
 --workpath temp/build^
 --add-data %UserProfile%\AppData\Roaming\Python\Python312\site-packages\customtkinter:customkinter\^
 --add-data temp/repository/metadata/root.json:.^
 --add-data ../src/assets:assets/^
 --add-data ../src/.env:.^
 --add-binary "nazaricklauncher.ico;."^
 --collect-all tkinterweb^
 --onedir^
 --windowed^
 --noconsole^
 --name "Nazarick Launcher"^
 F:\Projects\Active\nazarick-launcher\src\app.py

pause
