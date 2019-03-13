@echo off
set BASE_DIR=%~p0%
set PYFILE=%BASE_DIR%\bin\sapcli
if "%PYTHONPATH%"=="" (
    set PYTHONPATH=%BASE_DIR%
) else (
    if "x!PYTHONPATH:%BASE_DIR%=!"=="x%PYTHONPATH%" (
        set PYTHONPATH=%PYTHONPATH%;%BASE_DIR%
    )
)
echo %PYTHONPATH%
"py" -3 "%PYFILE%" %*