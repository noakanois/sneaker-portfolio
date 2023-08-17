from fastapi import APIRouter, HTTPException
from ..db_utils import DATABASE_PATH
from pydantic import BaseModel
import sqlite3
from api.img_utils import download_first_image, make_gif
from multiprocessing import Process

router_user = APIRouter()


class PortfolioData(BaseModel):
    userId: int
    shoeTitle: str
    shoeSize: float


@router_user.get("/users")
async def get_users():
    with sqlite3.connect(DATABASE_PATH) as conn:
        results = conn.cursor().execute("SELECT id, name FROM users").fetchall()
    return [{"id": r[0], "name": r[1]} for r in results]


@router_user.post("/user/addToPortfolio")
async def add_to_portfolio(data: PortfolioData):
    with sqlite3.connect(DATABASE_PATH) as conn:
        shoe_id, shoe_image_url = (
            conn.cursor()
            .execute("SELECT uuid,imageUrl FROM shoes WHERE title = ?", (data.shoeTitle,))
            .fetchone()
        )
      
        if not shoe_id:
            raise HTTPException(400, "Shoe not found")

        conn.cursor().execute(
            "INSERT INTO portfolios (user_id, shoe_id, shoe_size) VALUES (?, ?, ?)",
            (data.userId, shoe_id, data.shoeSize),
        )
        conn.commit()
        download_first_image(shoe_image_url, shoe_id) # Ensure we always have first image for showing in collection
        gif_process = Process(target=make_gif,args=(shoe_image_url, shoe_id))
        gif_process.start()
    return {"status": "success", "message": "Shoe added to portfolio successfully!"}


@router_user.delete("/user/{user_id}/portfolio/{urlKey}")
async def delete_from_portfolio(user_id: int, urlKey: str):
    with sqlite3.connect(DATABASE_PATH) as conn:
        shoe = (
            conn.cursor()
            .execute("SELECT uuid FROM shoes WHERE urlKey = ?", (urlKey,))
            .fetchone()
        )

        if not shoe:
            raise HTTPException(404, "Shoe not found")

        deleted_rows = (
            conn.cursor()
            .execute(
                "DELETE FROM portfolios WHERE user_id = ? AND shoe_id = ?",
                (user_id, shoe[0]),
            )
            .rowcount
        )
        conn.commit()

        if deleted_rows == 0:
            raise HTTPException(404, "Entry not found in portfolio")

    return {"status": "success", "message": "Shoe removed from portfolio successfully!"}
