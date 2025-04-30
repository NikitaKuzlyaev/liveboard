# auth.py
# app\auth\auth.py

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, Response, HTTPException, Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security.oauth2 import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from jose import JWTError
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import RedirectResponse

from app.db.database import get_db
from app.db.models import SiteUser, RegistrationConfirmation

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="", tags=["auth"])


class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        token = request.cookies.get("token")
        if token:
            return token

        return await super().__call__(request)


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/token")

# -------------------- Конфигурация ----------------------
SECRET_KEY = "i_hate_when_somebody_hugging_me"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# -------------------- Схемы ----------------------
class UserCreate(BaseModel):
    name: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    username: str


# ------------------------------------------------

@router.get('/auth/ping')
async def test():
    return 200, 'OK'


def hash_password(password: str) -> str:
    """"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
        data: dict,
        expires_delta: timedelta | None = None
) -> str:
    """
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    """"""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


@router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    """"""
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
async def login(request: Request):
    """"""
    return 200, 'Ok'


@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    """"""
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_model=Token)
async def register(
        user: UserCreate,
        db: AsyncSession = Depends(get_db)
):
    """
    """
    stmt = select(SiteUser).where(SiteUser.name == user.name)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

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
    return {"access_token": token, "token_type": "bearer", "username": new_user.name}


@router.post("/token", response_model=Token)
async def login_with_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    """
    """
    stmt = select(SiteUser).where(SiteUser.name == form_data.username)
    result = await db.execute(stmt)
    user: SiteUser = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.name}, expires_delta=access_token_expires
    )

    response = RedirectResponse("/", status_code=302)
    response.set_cookie(key="username", value=user.name, httponly=False)
    response.set_cookie(key="token", value=access_token, httponly=True)
    return response


@router.get("/logout")
async def logout(
        response: Response
):
    """
    """
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("username")
    response.delete_cookie("token")
    return response


@router.get("/me")
async def read_users_me(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
):
    """
    """
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


# @router.get("/confirm/{validation_string}", response_class=HTMLResponse)
# async def confirm_account(
#         validation_string: str
# ) -> Response:
#     """
#     """
#     result = await db.execute(select(RegistrationConfirmation).filter(RegistrationConfirmation.validation_string == validation_string))
#     confirm: RegistrationConfirmation = result.scalar_one_or_none()
#
#     site_user = await db.execute(select(SiteUser).filter(SiteUser.id == confirm.user_id)).scalar_one_or_none()
#
#     if not room:
#         raise HTTPException(status_code=404, detail="Confirm not found")
#
#     return templates.TemplateResponse("confirmed.html", {"request": request})
