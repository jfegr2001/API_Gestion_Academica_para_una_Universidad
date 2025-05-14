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
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)