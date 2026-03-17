from fastapi import FastAPI, status
from studies_api.routers import study_sessions, stats, users, auth

app = FastAPI(title="StudiesAPI")


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
