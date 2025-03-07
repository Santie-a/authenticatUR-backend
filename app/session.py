from itsdangerous import URLSafeTimedSerializer
from fastapi import Request, Response
from datetime import datetime, timezone, timedelta
from app.config import settings

# Create serializer for signing session tokens
serializer = URLSafeTimedSerializer(settings.SESSION_SECRET_KEY)

# Set session cookie
def create_session(response: Response, user_data: dict):    
    token = serializer.dumps(user_data)
    max_age = 3600

    expires = datetime.now(timezone.utc) + timedelta(seconds=max_age)

    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,  # Prevents JS access (XSS protection)
        secure=settings.SECURE_COOKIE,   # Set to True in production (for HTTPS)
        samesite=settings.SAME_SITE,
        max_age=max_age,
        expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        path="/"
    )

# Get session data
def get_session(request: Request):
    token = request.cookies.get("session_token")
    if not token:
        return None
    try:
        user_data = serializer.loads(token, max_age=3600)
        return user_data
    except Exception as e:
        return None

