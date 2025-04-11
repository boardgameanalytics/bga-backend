from fastapi import FastAPI

from web.routers.games import router as games_router  # type: ignore

app = FastAPI()

app.include_router(games_router)
