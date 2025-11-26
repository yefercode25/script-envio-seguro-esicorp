@echo off
title Sistema de Transferencia Segura - Launcher
color 0A

set VENV_DIR=venv
set REQUIREMENTS=requirements.txt

echo ====================================================
echo      INICIANDO SISTEMA DE TRANSFERENCIA SEGURA
echo ====================================================
echo.

REM 1. Verificar si existe Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no se encuentra en el PATH.
    echo Por favor instala Python y asegurate de marcar "Add Python to PATH".
    pause
    exit /b 1
)

REM 2. Verificar/Crear Entorno Virtual
if not exist %VENV_DIR% (
    echo [INFO] Entorno virtual no detectado. Creando 'venv'...
    python -m venv %VENV_DIR%
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    echo [OK] Entorno virtual creado exitosamente.
) else (
    echo [INFO] Entorno virtual detectado.
)

REM 3. Activar Entorno
echo [INFO] Activando entorno virtual...
call %VENV_DIR%\Scripts\activate.bat

REM 4. Instalar/Verificar Dependencias
echo [INFO] Verificando dependencias...
pip install -r %REQUIREMENTS% >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Hubo un problema instalando las dependencias.
    echo Intentando instalar mostrando el error...
    pip install -r %REQUIREMENTS%
    pause
    exit /b 1
)
echo [OK] Dependencias al dia.

REM 5. Iniciar Aplicación
echo.
echo [INFO] Iniciando aplicacion...
echo ----------------------------------------------------
python main.py

REM Finalización
echo.
echo [INFO] Sesion finalizada.
pause
