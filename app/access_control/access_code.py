import uuid
from datetime import datetime, timedelta, timezone
from app.database.supabase_client import supabase
from app.utils.jwt_token import generate_jwt, get_jwt_data, validate_token, validate_validator

def generate_access_code(user_id: str):
    """
    Generates a JWT based on the user_id and stores in db a code based on the user_id

    **Args**

    - **user_id**:
    User that requests the code
    """
    institution = user_id.split('@')[1].split('.')[0]
    r_id = uuid.uuid4().hex[:12]

    code = f"{institution}-{r_id}"

    token = generate_jwt({"token": code, "user_id": user_id})
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)

    # Store token in Supabase
    supabase.table("access_codes").insert({
        "user_id": user_id,
        "code": code,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "expires_at": expires_at.strftime("%Y-%m-%d %H:%M:%S"),
        "used": False
    }).execute()

    return token

def validate_access_code(token: str, validator_id: str, action: str) -> tuple[bool, str]:
    """
    Based on the JWT, validator id and action from the request generates a response and updates database

    **Args**

    - **token**:
    JWT detected by the physical device

    - **validator_id**:
    UUID sent by the physical device

    - **action**:
    Mode of the physical device (entry/exit)
    """
    payload = get_jwt_data(token)
    code = payload["token"]
    user_id = payload["user_id"]

    valid_validator, message_validator = validate_validator(validator_id, user_id)
    if not valid_validator:
        return False, message_validator
    
    valid_token, message_token = validate_token(code, user_id, action)
    if not valid_token:
        return False, message_token

    return True, "Valid Code"
