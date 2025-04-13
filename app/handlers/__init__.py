from handlers.ping import router as ping_router
from handlers.rooms import router as room_router

routers = [ping_router,
           room_router,
           ]