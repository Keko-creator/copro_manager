@echo off
rem ============================================
rem  Copro Manager - demarrage du serveur
rem  Premier double-clic : installe tout (env, .env)
rem  Double-clic suivants : lance le serveur
rem ============================================
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python est introuvable.
    echo Installez Python 3.12 depuis python.org et cochez
    echo "Add python.exe to PATH" pendant l'installation.
    pause
    exit /b 1
)

if not exist ".env" (
    if not exist ".env.example" (
        echo [ERREUR] Fichier .env.example introuvable.
        pause
        exit /b 1
    )
    echo [INFO] Creation du fichier .env depuis .env.example...
    copy /y ".env.example" ".env" >nul
    echo [ATTENTION] Pensez a ouvrir le fichier .env et a remplacer
    echo la SECRET_KEY par une valeur longue et unique.
)

if not exist "venv\Scripts\python.exe" (
    echo [INFO] Creation de l'environnement Python local...
    python -m venv venv
    if errorlevel 1 (
        echo [ERREUR] La creation de l'environnement a echoue.
        pause
        exit /b 1
    )
    echo [INFO] Installation des dependances (quelques minutes)...
    venv\Scripts\python -m pip install --upgrade pip
    venv\Scripts\pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERREUR] L'installation des dependances a echoue.
        pause
        exit /b 1
    )
)

echo [INFO] Demarrage du serveur. Laissez cette fenetre ouverte.
echo [INFO] Acces : http://localhost:5000
venv\Scripts\python.exe wsgi.py
pause
