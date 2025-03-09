import jwt
from datetime import datetime, timedelta, timezone
from app.config import settings

# Generate JWT
def create_jwt(user_data: dict):
    expiration = datetime.now(timezone.utc) + timedelta(hours=1)  # 1-hour expiry
    payload = {
        "exp": expiration,
        "iat": datetime.now(timezone.utc),
        "sub": user_data["username"],  # Unique user identifier
        "user_data": user_data  # Store additional user info
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")
    return token

# Decode and validate JWT
def verify_jwt(token: str):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return payload["user_data"]
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token
