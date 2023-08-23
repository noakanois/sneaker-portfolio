from fastapi import APIRouter, HTTPException
from ..db_utils import DATABASE_PATH
from pydantic import BaseModel
import sqlite3
import os
from api.img_utils import download_first_image, make_gif, get_images, delete_images, trim_image, IMAGE_PATH
from multiprocessing import Process

router_user = APIRouter()


class PortfolioData(BaseModel):
    userId: int
    shoeTitle: str


@router_user.get("/users")
async def get_users():
    with sqlite3.connect(DATABASE_PATH) as conn:
        results = conn.cursor().execute("SELECT id, name FROM users").fetchall()
    return [{"id": r[0], "name": r[1]} for r in results]


@router_user.post("/user/addToPortfolio")
async def add_to_portfolio(data: PortfolioData):
    with sqlite3.connect(DATABASE_PATH) as conn:
        shoe_uuid, shoe_image_url = (
            conn.cursor()
            .execute(
                "SELECT uuid,imageUrl FROM shoes WHERE title = ?", (data.shoeTitle,)
            )
            .fetchone()
        )

        if not shoe_uuid:
            raise HTTPException(400, "Shoe not found")

        conn.cursor().execute(
            "INSERT INTO portfolios (user_id, shoe_uuid) VALUES (?, ?)",
            (data.userId, shoe_uuid),
        )
        conn.commit()
        status = download_first_image(shoe_image_url,shoe_uuid)
        if status == "GIF":
            def download_images_and_create_gif(shoe_url,uuid):
                if get_images(shoe_image_url, shoe_uuid):
                    make_gif(shoe_image_url, shoe_uuid)
                    delete_images(shoe_uuid)
                trim_image(os.path.join(IMAGE_PATH, shoe_uuid, "img", "01.png"))
        gif_process = Process(target=download_images_and_create_gif, args=(shoe_image_url, shoe_uuid))
        gif_process.start()
    return {"status": "success", "message": "Shoe added to portfolio successfully!"}


@router_user.delete("/user/{user_id}/portfolio/{shoe_uuid}")
async def delete_from_portfolio(user_id: int, shoe_uuid: str):
    with sqlite3.connect(DATABASE_PATH) as conn:
        
        deleted_rows = (
            conn.cursor()
            .execute(
                "DELETE FROM portfolios WHERE user_id = ? AND shoe_uuid = ?",
                (user_id, shoe_uuid),
            )
            .rowcount
        )
        conn.commit()

        if deleted_rows == 0:
            raise HTTPException(404, "Entry not found in portfolio")

    return {"status": "success", "message": "Shoe removed from portfolio successfully!"}
