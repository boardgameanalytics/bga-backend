from fastapi import FastAPI

import app.db.models as models  # type: ignore
from app import config
from app.db.db_session import DatabaseSession  # type: ignore

app = FastAPI()

db = DatabaseSession(connection_string=config.db_url)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/games")
async def games():
    with db.get_session() as session:
        games = session.query(models.GameDetails).all()

    return games
