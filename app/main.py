# main.py
# app\main.py

import os
import sys
import logging
from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.db.init_db import init_models
from app.handlers import routers
from starlette.middleware.sessions import SessionMiddleware

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="1111")

templates = Jinja2Templates(directory="app/templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

for router in routers:
    app.include_router(router=router)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования (например, INFO, DEBUG, ERROR)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)

logger = logging.getLogger(__name__)
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

logger_registry = logging.root.manager.loggerDict
for logger_name, logger in logger_registry.items():
    if isinstance(logger, logging.Logger):
        if 'sqlalchemy' in logger_name or 'asyncpg' in logger_name:
            logging.getLogger(logger_name).setLevel(logging.WARNING)

        print(f"Logger Name: {logger_name}, Logger Level: {logging.getLevelName(logger.level)}")
    else:
        print(f"Logger Name: {logger_name} is a placeholder.")


@app.on_event("startup")
async def startup():
    await init_models()
    # print('I am alive!')
    logger.info('Hi!')
    logger.error('Hi!')
    logger.debug('Hi!')


@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    logger.info('main page')
    return templates.TemplateResponse("main.html", {"request": request})


"""

uvicorn app.main:app

"""
