from fastapi import APIRouter
from ..utils.db_utils import DATABASE_PATH
import sqlite3
from pydantic import BaseModel
from typing import List

router_portfolio = APIRouter()

QUERY_GET_PORTFOLIO = """
    SELECT 
        p.favorite, s.uuid, s.name, s.title, s.model, s.brand, s.urlKey, s.thumbUrl, s.smallImageUrl, s.imageUrl, s.description, s.retail_price, s.release_date, s.created_at
    FROM
        portfolios p
    JOIN 
        shoes s ON 
        p.shoe_uuid = s.uuid
    WHERE 
        p.user_id = ?
    ORDER BY
        p.order_position;
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
            "favorite": r[0],
            "uuid": r[1],
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


class ReorderPortfolio(BaseModel):
    shoe_uuids: List[str]


@router_portfolio.post("/user/{user_id}/portfolio/reorder")
async def reorder_portfolio(user_id: int, order_data: ReorderPortfolio):
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()

        for position, shoe_uuid in enumerate(order_data.shoe_uuids):
            cursor.execute(
                "UPDATE portfolios SET order_position = ? WHERE user_id = ? AND shoe_uuid = ?",
                (position, user_id, shoe_uuid),
            )

        conn.commit()

    return {"status": "success", "message": "Portfolio reordered successfully!"}
