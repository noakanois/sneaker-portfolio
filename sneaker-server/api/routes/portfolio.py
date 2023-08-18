from fastapi import APIRouter
from ..db_utils import DATABASE_PATH
import sqlite3

router_portfolio = APIRouter()

QUERY_GET_PORTFOLIO = """
    SELECT 
        p.shoe_size, p.favorite, s.uuid, s.name, s.title, s.model, s.brand, s.urlKey, s.thumbUrl, s.smallImageUrl, s.imageUrl, s.description, s.retail_price, s.release_date, s.created_at
    FROM
        portfolios p
    JOIN 
        shoes s ON 
        p.shoe_uuid = s.uuid
    WHERE 
        p.user_id = ?;
"""


@router_portfolio.get("/user/{user_id}/portfolio")
async def get_user_portfolio(user_id: int):
    with sqlite3.connect(DATABASE_PATH) as conn:
        results = (
            conn.cursor()
            .execute(
                QUERY_GET_PORTFOLIO,
                (user_id,),
            )
            .fetchall()
        )

    return [
        {
            "shoe_size": r[0],
            "favorite": r[1],
            "uuid": r[2],
            "name": r[3],
            "title": r[4],
            "model": r[5],
            "brand": r[6],
            "urlKey": r[7],
            "thumbUrl": r[8],
            "smallImageUrl": r[9],
            "imageUrl": r[10],
            "description": r[11],
            "retail_price": r[12],
            "release_date": r[13],
            "created_at": r[14],
        }
        for r in results
    ]
