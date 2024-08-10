from fastapi import FastAPI

import models
from database import engine
from routers import auth, todos, users

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


@app.get('/')
async def health_check():
    return {'message': 'System is up and running'}


app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(users.router)
