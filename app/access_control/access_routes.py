from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from app.auth.auth import profile  # Assuming JWT/session logic exists
from .access_code import generate_access_code, validate_access_code
from app.auth.auth import get_session

router = APIRouter()

@router.post("/generate-code")
def create_code(request: Request):
    session = get_session(request)
    if not session:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = generate_access_code(session["username"])
    return JSONResponse(content={"token": token})

@router.post("/validate-code/{token}") # It is necessary to increase the security here
def validate_code(token: str):
    is_valid, message = validate_access_code(token)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}

#@router.get("/generate-code-temp")
#def temp_generate_code(request: Request):
    """
    Temporary GET route for code validation.
    Example: /access/validate-code/abc123
    """
    session = get_session(request)
    if not session:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = generate_access_code(session["username"])
    return JSONResponse(content={"token": token})

#@router.get("/validate-code/{token}")
#def temp_validate_code(token: str):
    """
    Temporary GET route for code validation.
    Example: /access/validate-code/abc123
    """
    is_valid, message = validate_access_code(token)
    if not is_valid:
        return {"status": "error", "message": message}
    return {"status": "success", "message": message}