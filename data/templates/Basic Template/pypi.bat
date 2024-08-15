@echo off

echo INSTALLING PYPI LIBRARIES:
echo.

pip install -r .\build\pypi.txt

echo.
cd .\src\engine\gdf\
"pypi.bat"

echo.
pause
