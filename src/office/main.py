from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

import os
import django
from django.conf import settings

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'office.settings')
django.setup()

from office.endpoints import router as office_router
from employee.endpoints import router as employee_router
from workplace.endpoints import router as workplace_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # При запуске: инициализация
    print("Starting Office Management API...")
    yield
    # При остановке: очистка
    print("Shutting down Office Management API...")

app = FastAPI(
    title="Office Management API",
    description="Система управления офисами, сотрудниками и рабочими местами с Django моделями",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Настройка CORS для Windows development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(office_router, prefix="/api/v1/offices", tags=["offices"])
app.include_router(employee_router, prefix="/api/v1/employees", tags=["employees"])
app.include_router(workplace_router, prefix="/api/v1/workplaces", tags=["workplaces"])

@app.get("/")
async def root():
    return {"message": "Office Management System API with Django models"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "office-management"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)