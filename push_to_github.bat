@echo off
cd /d "%~dp0"
echo Envoi du projet vers https://github.com/bebeto55/Projet_qualite_air (branche main)...
git push -u origin main --force
pause
