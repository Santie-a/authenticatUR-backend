from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth.auth import router as auth_router
from app.access_control.access_routes import router as access_router
from app.config import settings

app = FastAPI()

# CORS settings (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],  # React frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routes
app.include_router(auth_router, prefix="/auth", tags=["Authorization"])
app.include_router(access_router, prefix="/access", tags=["Access Control"])

@app.get("/")
def read_root():
    return {"message": "FastAPI with Microsoft OAuth"}
