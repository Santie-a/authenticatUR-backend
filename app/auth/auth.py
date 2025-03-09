from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from msal import ConfidentialClientApplication
from datetime import timedelta, timezone, datetime
import uuid

from app.config import settings
from app.session import create_jwt, verify_jwt
from app.database.supabase_client import supabase
from app.utils.exchange_code import verify_exchange_code

router = APIRouter()

# MSAL App instance
msal_app = ConfidentialClientApplication(
    client_id=settings.CLIENT_ID,
    authority=settings.AUTHORITY,
    client_credential=settings.CLIENT_SECRET
)

# In-memory cache for simplicity (use Redis/DB in production)
state_cache = {}

@router.get("/login")
def login():
    # Generate unique state for CSRF protection
    state = str(uuid.uuid4())
    state_cache[state] = True

    auth_url = msal_app.get_authorization_request_url(
        scopes=[settings.SCOPE],
        state=state,
        redirect_uri=settings.REDIRECT_URI
    )
    return RedirectResponse(auth_url)

@router.get("/callback")
def callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    if state not in state_cache:
        raise HTTPException(status_code=400, detail="Invalid state")

    result = msal_app.acquire_token_by_authorization_code(
        code=code,
        scopes=[settings.SCOPE],
        redirect_uri=settings.REDIRECT_URI
    )

    if "access_token" in result:
        user_data = {
            "access_token": result["access_token"],
            "id_token": result.get("id_token"),
            "username": result.get("id_token_claims", {}).get("preferred_username")
        }

        expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

        supabase.table("exchange_codes").insert({
            "code": code,
            "user_id": result.get("id_token_claims", {}).get("preferred_username"),
            "expires_at": expires_at.strftime("%Y-%m-%d %H:%M:%S"),
        }).execute()

        # Redirect to frontend and pass the token in a response header
        response = RedirectResponse(url=f"{settings.FRONTEND_URL}?code={code}")
        return response
    else:
        raise HTTPException(status_code=400, detail="Token acquisition failed")


@router.get("/profile")
def profile(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = auth_header.split("Bearer ")[1]
    user_data = verify_jwt(token)

    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return JSONResponse(content={"message": "User Profile", "user": user_data})


@router.get("/logout")
def logout():
    return JSONResponse(content={"message": "Logout successful"})

@router.get("/exchange")
def exchange(request: Request):
    exchange_code_header = request.headers.get("ExchangeCode")
    if not exchange_code_header or not exchange_code_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    exchange_code = exchange_code_header.split("Bearer ")[1]

    username = verify_exchange_code(exchange_code)
    token = create_jwt({"username": username})

    return JSONResponse(content={"token": token})