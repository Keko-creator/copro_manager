@echo off
rem ============================================
rem  Copro Manager - lancement du serveur
rem  À exécuter sur le poste d'hébergement.
rem ============================================
chcp 65001 >nul
cd /d "%~dp0"

if not exist ".env" (
    echo [ERREUR] Fichier .env manquant.
    echo Copiez .env.example en .env et renseignez la SECRET_KEY.
    pause
    exit /b 1
)

if not exist "venv\Scripts\python.exe" (
    echo [ERREUR] Environnement virtuel introuvable.
    echo Exécutez d'abord INSTALLATION.md (étape création du venv).
    pause
    exit /b 1
)

venv\Scripts\python.exe wsgi.py
pause
