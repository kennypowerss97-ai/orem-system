from fastapi import Request, status
from fastapi.responses import JSONResponse

class OremException(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code

async def orem_exception_handler(request: Request, exc: OremException):
    return JSONResponse(status_code=exc.status_code, content={"message": exc.message})
