import jwt
from datetime import datetime, timezone
from app.config import settings
from app.database.supabase_client import supabase
from fastapi import HTTPException

def generate_jwt(payload: dict) -> str:
    """
    Generates a JWT based on a code and the user_id

    **Args**

    - **Payload**:
    Dict to save
    """
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token

def get_jwt_data(token: str) -> dict:
    """
    Decodes a JWT and returns its data.
    
    Returns a Dict if the token is valid. Otherwise raises an HTTP Exception

    **Args**

    - **token**:
    Token coded as a JWT
    """
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid token: {str(e)}"
        )

def validate_token(code: str, user_id: str, action: str) -> tuple[bool, str]:
    """
    Validates the JWT scanned by a physical device

    **Args**

    - **code**:
    Code decoded by JWT

    - **user_id**
    user_id assosiated with the JWT

    - **action**:
    Mode of the physical device (entry/exit) 
    """

    # Verify token access restrictions
    try:
        response_code = supabase.table("access_codes").select("*").eq("code", code).single().execute()
        token_record = response_code.data
    except:
        token_record = None

    if not token_record:
        return False, "Invalid code"

    if token_record["used"]:
        return False, "Code already used"

    if datetime.now(timezone.utc) > datetime.strptime(token_record["expires_at"], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc):
        return False, "Code expired"
    
    # Verify user access restrictions
    try:
        response_user_id = supabase.table("access_codes").select("*").eq("user_id", user_id).eq("used", True).order("created_at", desc=True).limit(1).single().execute()
        user_id_record = response_user_id.data
    except:
        user_id_record = None

    if user_id_record:
        if user_id_record["action"] == "entry" and action == "entry":
            return False, "Invalid action"
        
        if user_id_record["action"] == "exit" and action == "exit":
            return False, "Invalid action"

    # Mark code as used
    supabase.table("access_codes").update({"used": True, "action": action}).eq("id", token_record["id"]).execute()

    return True, "Success"

def validate_validator(validator_id: str, user_id: str) -> tuple[bool, str]:
    """
    Validates the physical device and the user

    **Args**

    - **validator_id**:
    Code decoded by JWT

    - **user_id**
    user_id assosiated with the JWT
    """
    user_institution = user_id.split("@")[1].split(".")[0]

    try:
        response_validator = supabase.table("validators").select("*").eq("id", validator_id).single().execute()
        validator_record = response_validator.data
    except:
        validator_record = None

    if validator_record:
        if validator_record["institution"] != user_institution:
            return False, "Institution error"
        
        return True, "Validator success"
    else:
        return False, "Validator error"