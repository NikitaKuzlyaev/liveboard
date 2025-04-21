import logging

from fastapi import Depends, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Request, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from app.handlers import routers
from app.db.database import get_db
from app.db.init_db import init_models
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from fastapi import FastAPI, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import select
from app.db.models import Room, RoomUser, SiteUser
import sys
from app.handlers.auth import hash_password, create_access_token, verify_password, decode_access_token
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

for router in routers:
    app.include_router(router=router)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# -------------------- Схемы ----------------------

class UserCreate(BaseModel):
    name: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# ------------------------------------------------
@app.on_event("startup")
async def startup():
    await init_models()
    print('I am alive!')


@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def login(request: Request):
    return 200, 'Ok'


@app.get("/register", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register", response_model=Token)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    stmt = select(SiteUser).where(SiteUser.name == user.name)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    #logging.log(msg=f"{user.name} {user.password}", level=0)

    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    new_user = SiteUser(
        name=user.name,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    token = create_access_token(data={"sub": new_user.name})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    stmt = select(SiteUser).where(SiteUser.name == form_data.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    token = create_access_token(data={"sub": user.name})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/me")
async def read_users_me(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Недействительный токен")
    except JWTError:
        raise HTTPException(status_code=401, detail="Недействительный токен")

    stmt = select(SiteUser).where(SiteUser.name == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return {"id": user.id, "name": user.name}


"""

uvicorn app.main:app

"""
