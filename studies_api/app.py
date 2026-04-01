from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from studies_api.routers import auth, stats, study_sessions, users

app = FastAPI(title='StudiesAPI')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:5500',
        'http://127.0.0.1:5500',
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'null',  # para file:// protocol durante desenvolvimento
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


app.include_router(
    router=auth.router,
    prefix='/api/v1/auth',
    tags=['Authentication'],
)

app.include_router(
    router=users.router,
    prefix='/api/v1/users',
    tags=['Users'],
)

app.include_router(
    router=study_sessions.router,
    prefix='/api/v1/sessions',
    tags=['Sessions'],
)

app.include_router(
    router=stats.router,
    prefix='/api/v1/stats',
    tags=['Stats'],
)


@app.get('/health_check', status_code=status.HTTP_200_OK, tags=['Health Check'])
def health_check():
    return {'status': 'OK'}
