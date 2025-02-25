from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.responses import RedirectResponse, JSONResponse
from msal import ConfidentialClientApplication
from app.config import settings
from app.session import create_session, get_session
import uuid

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
def callback(request: Request, response: Response):
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

        # Create the session cookie
        create_session(response, user_data)

        # Create redirect response AFTER setting the cookie
        redirect_response = RedirectResponse(url="/auth/profile")
        create_session(redirect_response, user_data)  # Attach cookie to the redirect response
        return redirect_response
    else:
        raise HTTPException(status_code=400, detail="Token acquisition failed")


@router.get("/profile")
def profile(request: Request):
    session = get_session(request)
    if not session:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return JSONResponse(content={"message": "User Profile", "user": session})

@router.get("/logout")
def logout(response: Response):
    response = RedirectResponse(url="/")
    response.delete_cookie("session_token")
    return response

