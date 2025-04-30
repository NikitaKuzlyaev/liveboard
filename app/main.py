import os
import sys

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


@app.on_event("startup")
async def startup():
    await init_models()
    print('I am alive!')


@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})


"""

uvicorn app.main:app

"""
