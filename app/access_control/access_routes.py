from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from .access_code import generate_access_code, validate_access_code
from app.session import verify_jwt
from app.utils.api_security import validate_api_key

router = APIRouter()

@router.post("/generate-code")
def create_code(request: Request):
    """
    POST route for code creation.
    It requires to be authenticated in order to POST
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = auth_header.split("Bearer ")[1]
    user_data = verify_jwt(token)

    if not user_data:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    token = generate_access_code(user_data["username"])
    return JSONResponse(content={"token": token})

@router.post("/validate-code") # It is necessary to increase the security here
async def validate_code(request: Request, api_key: str = Depends(validate_api_key)):
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
    
    return {"detail": message}