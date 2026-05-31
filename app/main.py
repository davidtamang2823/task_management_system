from fastapi import FastAPI
from user.entrypoint.routes import user_router
from task.entrypoints.routes import task_router
from middlewares.auth_middleware import JWTAuthMiddleware

app = FastAPI()

app.add_middleware(JWTAuthMiddleware)

app.include_router(user_router)
app.include_router(task_router)

