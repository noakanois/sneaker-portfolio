from fastapi import APIRouter
from ..utils.db_utils import DATABASE_PATH
import sqlite3
from pydantic import BaseModel
from typing import List

router_favorite = APIRouter()


@router_favorite.post("/favorites/{user_id}/set/{shoe_uuid}/{status}")
async def set_favorite(user_id: int, shoe_uuid: str, status: bool):
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE portfolios SET favorite = ? WHERE user_id = ? AND shoe_uuid = ?",
            (status, user_id, shoe_uuid),
        )
        conn.commit()

    return {"status": "success", "message": "Favorite set succesfully!"}
