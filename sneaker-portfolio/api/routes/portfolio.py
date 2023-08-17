from fastapi import APIRouter
from ..db_utils import DATABASE_PATH
import sqlite3

router_portfolio = APIRouter()

QUERY_GET_PORTFOLIO = """
    SELECT 
        p.shoe_size, p.favorite, s.name, s.title, s.model, s.brand, s.urlKey, s.thumbUrl, s.smallImageUrl, s.imageUrl, s.description, s.retail_price, s.release_date, s.created_at
    FROM
        portfolios p
    JOIN 
        shoes s ON 
        p.shoe_id = s.id
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
            "name": r[2],
            "title": r[3],
            "model": r[4],
            "brand": r[5],
            "urlKey": r[6],
            "thumbUrl": r[7],
            "smallImageUrl": r[8],
            "imageUrl": r[9],
            "description": r[10],
            "retail_price": r[11],
            "release_date": r[12],
            "created_at": r[13],
        }
        for r in results
    ]
