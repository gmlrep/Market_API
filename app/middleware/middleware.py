import logging
from fastapi import Request


logger_error_400 = logging.getLogger('error_4xx')
logger_error_400.setLevel(logging.INFO)
handler_error4 = logging.FileHandler('logs/error_4xx.log')
handler_error4.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler_error4.setFormatter(formatter)

logger_error_500 = logging.getLogger('error_5xx')
logger_error_500.setLevel(logging.INFO)
handler_error5 = logging.FileHandler('logs/error_5xx.log')
handler_error5.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler_error5.setFormatter(formatter)


logger_error_400.addHandler(handler_error4)
logger_error_500.addHandler(handler_error5)


async def logging_middleware(request: Request, call_next):
    response = await call_next(request)

    if 400 <= response.status_code <= 499:
        logger_error_400.info(f"Incoming request: {request.method} {request.url.path}")
        logger_error_400.info(f"Outgoing response code: {response.status_code}")

    if 500 <= response.status_code <= 599:
        logger_error_500.info(f"Incoming request: {request.method} {request.url.path}")
        logger_error_500.info(f"Outgoing response code: {response.status_code}")

    return response
