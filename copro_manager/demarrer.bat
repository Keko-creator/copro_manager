@echo off
rem ============================================
rem  Copro Manager - demarrage du serveur
rem  Journal detaille : demarrage.log
rem  Premier lancement : installe tout automatiquement
rem ============================================
cd /d "%~dp0"
set "LOG=%~dp0demarrage.log"
echo ===== Demarrage de Copro Manager ===== > "%LOG%"
echo Date : %date% %time% >> "%LOG%"

rem --- Etape 1 : trouver Python (py -3 ou python) ---
echo Etape 1/5 : recherche de Python >> "%LOG%"
set "PYCMD="
py -3 -c "print('ok')" >> "%LOG%" 2>&1
if not errorlevel 1 set "PYCMD=py -3"
if not defined PYCMD (
    python -c "print('ok')" >> "%LOG%" 2>&1
    if not errorlevel 1 set "PYCMD=python"
)
if not defined PYCMD (
    echo [ERREUR] Python est introuvable. >> "%LOG%"
    echo.
    echo [ERREUR] Python n'est pas installe ou absent du PATH.
    echo 1. Installez Python 3.12 : https://www.python.org/downloads/
    echo 2. Pendant l'installation, cochez "Add python.exe to PATH".
    echo 3. Relancez ce fichier.
    echo.
    echo Details dans le fichier : demarrage.log
    echo.
    pause
    exit /b 1
)
echo Python trouve : %PYCMD% >> "%LOG%"

rem --- Etape 2 : fichier .env ---
echo Etape 2/5 : fichier .env >> "%LOG%"
if not exist ".env" (
    if exist ".env.example" (
        copy /y ".env.example" ".env" >nul
        echo Fichier .env cree depuis .env.example >> "%LOG%"
    ) else (
        echo [ERREUR] .env.example introuvable >> "%LOG%"
        echo.
        echo [ERREUR] Fichier .env.example introuvable.
        echo Le dossier de l'application est-il complet ?
        echo.
        pause
        exit /b 1
    )
)
echo Fichier .env OK >> "%LOG%"

rem --- Etape 3 : environnement Python local (venv) ---
echo Etape 3/5 : environnement Python local >> "%LOG%"
if not exist "venv\Scripts\python.exe" (
    echo [INFO] Creation de l'environnement Python local. Patientez...
    %PYCMD% -m venv venv >> "%LOG%" 2>&1
    if not exist "venv\Scripts\python.exe" (
        echo [ERREUR] Creation du venv echouee >> "%LOG%"
        echo.
        echo [ERREUR] La creation de l'environnement Python a echoue.
        echo Consultez le fichier : demarrage.log
        echo.
        pause
        exit /b 1
    )
)
echo Environnement Python OK >> "%LOG%"

rem --- Etape 4 : dependances (une seule fois) ---
echo Etape 4/5 : dependances Python >> "%LOG%"
if not exist "venv\.dependances-installees" (
    echo [INFO] Installation des dependances. Patientez quelques minutes...
    venv\Scripts\python -m pip install --upgrade pip >> "%LOG%" 2>&1
    venv\Scripts\pip install -r requirements.txt >> "%LOG%" 2>&1
    if errorlevel 1 (
        echo [ERREUR] Installation des dependances echouee >> "%LOG%"
        echo.
        echo [ERREUR] L'installation des dependances a echoue.
        echo Consultez le fichier : demarrage.log
        echo.
        pause
        exit /b 1
    )
    echo ok > "venv\.dependances-installees"
)
echo Dependances OK >> "%LOG%"

rem --- Etape 5 : serveur ---
echo Etape 5/5 : demarrage du serveur >> "%LOG%"
echo.
echo [INFO] Demarrage du serveur...
echo [INFO] Acces : http://localhost:5000
echo [INFO] Laissez cette fenetre ouverte. CTRL+C pour arreter.
echo.
venv\Scripts\python.exe wsgi.py
echo.
echo [INFO] Le serveur s'est arrete.
echo En cas d'erreur, consultez le fichier : demarrage.log
echo.
pause
