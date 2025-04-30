# rooms.py
# app/handlers/rooms.py

import logging
from uuid import UUID
from uuid import uuid4

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Request, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.database import get_db
from app.db.models import Room, RoomUser, SiteUser
from app.tasks.tasks import delete_room_task
from app.auth.dependencies import get_current_user

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/room", tags=["room"])

active_connections = {}  # Храним все подключения к комнате в словаре

# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@router.post('/')
async def create_new_room(
        user: SiteUser = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    """
    room_uuid = uuid4()
    room = Room(uuid=room_uuid, is_open=True, creator_id=user.id)

    db.add(room)
    await db.commit()

    logger.info(f"Before delete_room_task")
    delete_room_task.apply_async(args=[room.uuid], countdown=10)
    logger.info(f"under delete_room_task")

    return RedirectResponse(url=f"/room/{room.uuid}", status_code=302)


@router.get("/{room_uuid}", response_class=HTMLResponse)
async def room_page(
        room_uuid: UUID,
        request: Request,
        db: AsyncSession = Depends(get_db)
):
    """
    """
    # Выполняем запрос для получения комнаты с указанным UUID
    result = await db.execute(select(Room).filter(Room.uuid == room_uuid))
    room = result.scalar_one_or_none()  # Получаем одну запись или None, если комната не найдена

    if not room:
        # Если комната не найдена, возвращаем ошибку 404 (можно сделать редирект или вывести сообщение)
        raise HTTPException(status_code=404, detail="Room not found")

    # Передаем uuid комнаты в шаблон
    return templates.TemplateResponse("room.html", {"request": request, "room_uuid": room_uuid})


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
