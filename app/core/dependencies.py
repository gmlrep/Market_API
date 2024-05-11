from fastapi import FastAPI, Depends, HTTPException, Request, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import decode_jwt


def verify_jwt(jwt_token: str) -> bool:
    is_token_valid: bool = False

    try:
        payload = decode_jwt(jwt_token)
    except:
        payload = None
    if payload:
        is_token_valid = True
    return is_token_valid


class JWTBearer(HTTPBearer):
    def __init__(self, access_token=Cookie(), auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)
        self.access_token = access_token

    async def __call__(self, request: Request):
        # credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        credentials = self.access_token
        # if credentials:
            # if not credentials.scheme == "Bearer":
            #     raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
        #     if not verify_jwt(credentials.credentials):
        #         raise HTTPException(status_code=403, detail="Invalid token or expired token.")
        #     return credentials.credentials
        # else:
        #     raise HTTPException(status_code=403, detail="Invalid authorization code.")
