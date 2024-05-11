from fastapi import Request
from fastapi.responses import JSONResponse


# кастомный обработчик исключения для всех HTTPException
async def custom_http_exception_handler(request: Request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'status': 'error',
            'data': None,
            'details': exc.detail
        })
