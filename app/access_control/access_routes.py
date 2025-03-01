from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from app.auth.auth import profile  # Assuming JWT/session logic exists
from .access_code import generate_access_code, validate_access_code
from app.auth.auth import get_session

router = APIRouter()

@router.post("/generate-code")
def create_code(request: Request):
    """
    POST route for code creation.
    It requires to be authenticated in order to POST
    """
    session = get_session(request)
    if not session:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = generate_access_code(session["username"])
    return JSONResponse(content={"token": token})

@router.post("/validate-code") # It is necessary to increase the security here
async def validate_code(request: Request):
    """
    POST route for code validation. In the body of the request is the token, UUID of the validator and mode.
    """
    body = await request.json()
    token = body.get("token")
    validator_id = body.get("validator_id")
    action = body.get("action")

    if not token or not validator_id or not action:
        raise HTTPException(status_code=400, detail="Details are missing")

    is_valid, message = validate_access_code(token, validator_id, action)

    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    return {"message": message}