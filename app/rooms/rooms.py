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
from app.db.models import Room, RoomUser
from app.tasks.tasks import delete_room_task

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(prefix="/room", tags=["room"])

# Храним все подключения к комнате в словаре
active_connections = {}

# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)  # Устанавливаем уровень логирования


@router.post('/')
async def create_new_room(name: str = Form(...), db: AsyncSession = Depends(get_db)):
    # Генерация UUID для комнаты
    room_uuid = uuid4()

    # Создание пользователя и комнаты
    room_user = RoomUser(name=name, room_id=room_uuid)
    room = Room(uuid=room_uuid, is_open=True, creator_id=None)

    # Сохраняем пользователя и комнату в базе данных
    db.add_all([room, room_user])
    await db.commit()

    # Связываем комнату с пользователем через creator_id
    room.creator_id = room_user.id
    await db.commit()

    logger.info(f"Before delete_room_task")
    delete_room_task.apply_async(args=[room.uuid], countdown=10)
    # delete_room_task.apply_async(args=[room.uuid])
    logger.info(f"under delete_room_task")

    return RedirectResponse(url=f"/room/{room.uuid}", status_code=302)


@router.get("/{room_uuid}", response_class=HTMLResponse)
async def room_page(room_uuid: UUID, request: Request, db: AsyncSession = Depends(get_db)):
    # Выполняем запрос для получения комнаты с указанным UUID
    result = await db.execute(select(Room).filter(Room.uuid == room_uuid))
    room = result.scalar_one_or_none()  # Получаем одну запись или None, если комната не найдена

    if not room:
        # Если комната не найдена, возвращаем ошибку 404 (можно сделать редирект или вывести сообщение)
        raise HTTPException(status_code=404, detail="Room not found")

    # Передаем uuid комнаты в шаблон
    return templates.TemplateResponse("room.html", {"request": request, "room_uuid": room_uuid})


@router.websocket("/ws/{room_uuid}")
async def websocket_endpoint(websocket: WebSocket, room_uuid: str):
    # Ожидаем подключения клиента
    await websocket.accept()

    # Добавляем клиента в активные соединения
    if room_uuid not in active_connections:
        active_connections[room_uuid] = []

    active_connections[room_uuid].append(websocket)

    try:
        while True:
            # Ожидаем сообщения от клиента
            message = await websocket.receive_text()

            # Рассылаем сообщение всем подключенным клиентам этой комнаты
            for connection in active_connections[room_uuid]:
                if connection != websocket:
                    await connection.send_text(message)
    except WebSocketDisconnect:
        # Убираем подключение из активных при отключении
        active_connections[room_uuid].remove(websocket)
        if not active_connections[room_uuid]:
            del active_connections[room_uuid]


@router.get('/')
async def connect_room():
    return 200, {'message': 'ok. it works'}
