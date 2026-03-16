from fastapi import FastAPI, status
from studies_api.routers import study_sessions, stats, users

app = FastAPI(title="StudiesAPI")


@app.get('/health_check', status_code=status.HTTP_200_OK)
def health_check():
    return {'status': 'OK'}


app.include_router(
    router=users.router,
    prefix='/api/v1/users',
    tags=['users'],
)

app.include_router(
    router=study_sessions.router,
    prefix='/api/v1/sessions',
    tags=['sessions'],
)

app.include_router(
    router=stats.router,
    prefix='/api/v1/stats',
    tags=['stats'],
)
