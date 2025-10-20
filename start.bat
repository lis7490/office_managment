@echo off
chcp 65001 >nul
echo Starting Office Management System with Django models...
echo.

echo Checking Docker...
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker Desktop is not running!
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo Building and starting services...
docker-compose up -d

echo Waiting for services to initialize...
timeout /t 20 /nobreak >nul

echo Checking services status...
docker-compose ps

echo.
echo ===================================================
echo Office Management System is ready!
echo ===================================================
echo API Server:    http://localhost:8000
echo Swagger Docs:  http://localhost:8000/api/docs
echo PostgreSQL:    localhost:5432
echo.
echo Features:
echo - Employee management with validation rules
echo - Desk reservation system  
echo - Skills management
echo - Automatic developer/tester separation
echo ===================================================

echo.
echo Press any key to open Swagger documentation...
pause >nul
start http://localhost:8000/api/docs