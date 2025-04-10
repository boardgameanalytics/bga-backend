from fastapi import FastAPI

from app.db.db_session import db  # type: ignore
import app.db.models as models  # type: ignore

app = FastAPI()


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
