from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel, OAuthFlowAuthorizationCode
from fastapi.security import OAuth2
from app.auth.auth import router as auth_router
from app.access_control.access_routes import router as access_router

app = FastAPI()

# CORS settings (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:8000"],  # React frontend URL
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
