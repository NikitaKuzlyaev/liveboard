
from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from app.handlers import routers

from app.db.database import get_db
from app.db.models import Room, User
from app.db.init_db import init_models

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

for router in routers:
    app.include_router(router=router)


@app.on_event("startup")
async def startup():

    await init_models()
    print('DB IS OK!!!')


@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})


"""

uvicorn app.main:app

"""
