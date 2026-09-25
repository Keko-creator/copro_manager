@echo off
rem ============================================
rem  Copro Manager - sauvegarde de la base
rem  À planifier chaque jour dans le Planificateur
rem  de tâches Windows (voir INSTALLATION.md).
rem ============================================
chcp 65001 >nul
cd /d "%~dp0"

set DOSSIER=..\sauvegardes
if not exist "%DOSSIER%" mkdir "%DOSSIER%"

for /f "tokens=1-3 delims=/" %%a in ("%date:~0,10%") do set JOUR=%%c-%%a-%%b
set HEURE=%time:~0,2%%time:~3,2%
set HEURE=%HEURE: =0%

copy /y "instance\copro_manager.db" "%DOSSIER%\copro_manager_%JOUR%_%HEURE%.db" >nul

rem Ne garder que les 30 dernières sauvegardes
for /f "skip=30 delims=" %%f in ('dir /b /o-d /a-d "%DOSSIER%\copro_manager_*.db" 2^>nul') do del "%DOSSIER%\%%f"
