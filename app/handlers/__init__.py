from app.handlers.ping import router as ping_router
from app.handlers.rooms import router as room_router
from app.auth.auth import router as auth_router


routers = [ping_router,
           room_router,
           auth_router,
           ]