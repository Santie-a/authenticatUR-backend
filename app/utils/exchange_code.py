from fastapi import HTTPException
from app.database.supabase_client import supabase

def verify_exchange_code(code: str):
    try:
        response_code = supabase.table("exchange_codes").select("*").eq("code", code).single().execute()
        code_record = response_code.data
    except:
        code_record = None

    if code_record:
        supabase.table("exchange_codes").delete().eq("code", code).execute()
        return code_record["user_id"]
    else:
        raise HTTPException(status_code=400, detail="Invalid Exchange Code")