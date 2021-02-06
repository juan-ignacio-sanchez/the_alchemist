@ECHO OFF
echo This script will do the following operations:
echo 1. Upgrade pip3 to the latest version
echo 2. Install pipenv to manage virtual environments
echo 3. Install all the dependencies for 'The Alchemist'
echo.

:choice
set /P c=Are you sure? [y/n]
if /I "%c%" EQU "Y" goto :run
if /I "%c%" EQU "N" goto :exit
goto :choice

:run
@ECHO ON
python3 -m pip install --upgrade pip
python3 -m pip install pipenv
python3 -m pipenv install

:exit
@ECHO OFF
echo.
echo =================================================
echo Installation completed.
echo You can run the game by executing run-win.bat
echo Press any key to exit.
pause > nul