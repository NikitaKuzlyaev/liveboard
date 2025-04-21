from .ping import router as ping_router
from .rooms import router as room_router
from .auth import router as auth_router


routers = [ping_router,
           room_router,
           auth_router,
           ]