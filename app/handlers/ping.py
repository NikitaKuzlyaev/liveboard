from fastapi import FastAPI, APIRouter

router = APIRouter(prefix="/ping", tags=["ping"])


@router.get('/db')
async def ping_db():
    return 200, {'message': 'ok. it works'}


@router.get('/app')
async def ping_app():
    return 200, {'message': 'ok. it works'}
