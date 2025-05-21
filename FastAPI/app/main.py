# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

# Import routers
from routes.auth import router as auth_router
from routes.users import router as users_router
from routes.academic import (
    router as academic_router,
    semester_router,
    subject_router,
    schedule_router,
    enrollment_router,
    grade_router
)

app = FastAPI(
    title="Sistema de Gestión Académica",
    description="API para la gestión académica universitaria",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(academic_router, prefix=settings.API_V1_STR)
app.include_router(semester_router, prefix=f"{settings.API_V1_STR}")
app.include_router(subject_router, prefix=f"{settings.API_V1_STR}")
app.include_router(schedule_router, prefix=f"{settings.API_V1_STR}")
app.include_router(enrollment_router, prefix=f"{settings.API_V1_STR}")
app.include_router(grade_router, prefix=f"{settings.API_V1_STR}")

@app.get("/")
def root():
    return {"message": "Bienvenido al Sistema de Gestión Académica"}

