import web.db.models as models  # type: ignore
from common import config  # type: ignore
from fastapi import APIRouter
from web.db.session import DatabaseSession  # type: ignore

router = APIRouter()

db = DatabaseSession(connection_string=config.db_url)


@router.get("/games")
async def games():
    with db.get_session() as session:
        games = session.query(models.GameDetails).all()

    return games
