import uuid
from datetime import datetime, timedelta, timezone
from app.database.supabase_client import supabase

def generate_access_code(user_id: str):
    institution = user_id.split('@')[1].split('.')[0]

    token = f"{institution}-{str(uuid.uuid4())[:12]}"
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)  # 5 min expiry

    # Store token in Supabase
    supabase.table("access_codes").insert({
        "user_id": user_id,
        "token": token,
        "expires_at": expires_at.strftime("%Y-%m-%d %H:%M:%S"),
        "used": False
    }).execute()

    return token

def validate_access_code(token: str):
    response = supabase.table("access_codes").select("*").eq("token", token).single().execute()
    record = response.data

    if not record:
        return False, "Invalid code"

    if record["used"]:
        return False, "Code already used"

    if datetime.now(timezone.utc) > datetime.strptime(record["expires_at"], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc):
        return False, "Code expired"

    # Mark code as used
    supabase.table("access_codes").update({"used": True}).eq("id", record["id"]).execute()

    return True, "Access granted"
