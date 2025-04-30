# rooms.py
# app\handlers\rooms.py

import logging
from uuid import UUID
from uuid import uuid4
import colorlog
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.db.models import Room, RoomUser, SiteUser
from app.tasks.tasks import delete_room_task
from app.auth.dependencies import get_current_user
from app.db.crud.room import create_room, get_room_by_uuid, get_list_of_rooms_by_user

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/room", tags=["room"])

active_connections = {}

logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)

handler = colorlog.StreamHandler()

formatter = colorlog.ColoredFormatter(
    '%(log_color)s%(levelname)-8s%(reset)s %(message)s',
    datefmt=None,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'cyan',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
    },
)

handler.setFormatter(formatter)
logger.addHandler(handler)


@router.post('/')
async def create_new_room(
        user: SiteUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    """
    """
    logger.info('i am in create_new_room')
    room = await create_room(session=db, user=user)
    delete_room_task.apply_async(args=[room.uuid], countdown=7200)
    return RedirectResponse(url=f"/room/page/{room.uuid}", status_code=302)


@router.get("/page/{room_uuid}", response_class=HTMLResponse)
async def room_page(
        room_uuid: UUID,
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    """
    """
    logger.info('i am in room_page')
    room = await get_room_by_uuid(session=db, room_uuid=room_uuid)
    if not room:
        raise HTTPException(status_code=404, detail="Комната не найдена")
    return templates.TemplateResponse("room.html", {"request": request, "room_uuid": room_uuid})


@router.get("/my", response_class=HTMLResponse)
async def get_user_rooms(
        request: Request,
        user: SiteUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    """
    """
    logger.info('i am in get_user_rooms')
    rooms_uuid = await get_list_of_rooms_by_user(session=db, user=user)
    return templates.TemplateResponse("my_rooms.html", {"request": request, "rooms_uuid": rooms_uuid})


@router.websocket("/ws/{room_uuid}")
async def websocket_endpoint(
        websocket: WebSocket,
        room_uuid: str
):
    """
    """
    await websocket.accept()  # Ожидаем подключения клиента

    if room_uuid not in active_connections:  # Добавляем клиента в активные соединения
        active_connections[room_uuid] = []

    active_connections[room_uuid].append(websocket)

    try:
        while True:
            message = await websocket.receive_text()  # Ожидаем сообщения от клиента
            # Рассылаем сообщение всем подключенным клиентам этой комнаты
            for connection in active_connections[room_uuid]:
                if connection != websocket:
                    await connection.send_text(message)

    except WebSocketDisconnect:
        active_connections[room_uuid].remove(websocket)  # Убираем подключение из активных при отключении
        if not active_connections[room_uuid]:
            del active_connections[room_uuid]


@router.get('/')
async def connect_room():
    return 200, {'message': 'ok. it works'}
