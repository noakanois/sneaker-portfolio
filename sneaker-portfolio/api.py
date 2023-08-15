from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import datetime
from scrape import get_search_json
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from image import *
from multiprocessing import Process
import uuid

app = FastAPI()

app.mount("/static", StaticFiles(directory="../sn-frontend/build/static"), name="static")

from fastapi import HTTPException

@app.get("/")
def serve_root_files():
    return FileResponse("../sn-frontend/build/index.html")

@app.get("/manifest.json")
def serve_manifest():
    return FileResponse("../sn-frontend/build/manifest.json")

@app.get("/logo192.png")
def serve_logo():
    return FileResponse("../sn-frontend/build/logo192.png")

DATABASE_PATH = "test.db"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def execute_sql(file_path):
    with open(file_path, "r") as f, sqlite3.connect(DATABASE_PATH) as conn:
        conn.cursor().executescript(f.read())
        conn.commit()


def table_empty(table):
    with sqlite3.connect(DATABASE_PATH) as conn:
        row_count = conn.cursor().execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    return row_count == 0


@app.on_event("startup")
async def startup_db():
    schema_files = [
        "db_model/schema/users.sql",
        "db_model/schema/portfolios.sql",
        "db_model/schema/shoes.sql",
    ]
    data_files = [
        "db_model/data/user_data.sql",
        "db_model/data/shoe_data.sql",
        "db_model/data/portfolio_data.sql",
    ]
    tables = ["users", "shoes", "portfolios"]

    for file in schema_files:
        execute_sql(file)

    for file, table in zip(data_files, tables):
        if table_empty(table):
            execute_sql(file)


@app.get("/users")
async def get_users():
    with sqlite3.connect(DATABASE_PATH) as conn:
        results = conn.cursor().execute("SELECT id, name FROM users").fetchall()
    return [{"id": r[0], "name": r[1]} for r in results]


@app.get("/user/{user_id}/portfolio")
async def get_user_portfolio(user_id: int):
    with sqlite3.connect(DATABASE_PATH) as conn:
        results = conn.cursor().execute(
            """

            SELECT p.shoe_size, p.favorite, s.uuid, s.name, s.title, s.model, s.brand, s.urlKey, s.thumbUrl, s.smallImageUrl, s.imageUrl, s.description, s.retail_price, s.release_date, s.created_at
            FROM portfolios p
            JOIN shoes s ON p.shoe_id = s.uuid
            WHERE p.user_id = ?
        """, (user_id,)
        ).fetchall()

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


@app.get("/search/name/{name}")
def search_name(name: str):
    results = get_search_json(name)

    with sqlite3.connect(DATABASE_PATH) as conn:
        for r in results:
            unique_ID = uuid.uuid5(uuid.NAMESPACE_X500, f"{r['title']}{r['urlKey']}")
         
            conn.cursor().execute(
                """
                INSERT OR IGNORE INTO shoes (uuid, name, title, model, brand, urlKey, thumbUrl, smallImageUrl, imageUrl,
                                  description, retail_price, release_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                    str(unique_ID),
                    r["name"],
                    r["title"],
                    r["model"],
                    r["brand"],
                    r["urlKey"],
                    r["thumbUrl"],
                    r["smallImageUrl"],
                    r["imageUrl"],
                    r["description"],
                    r["retailPrice"],
                    r["releaseDate"],
                    datetime.datetime.now(),
                )
            )
        conn.commit()

    return results



@app.get("/images/uuid/{uuid}/gif")
def search_name(uuid: str):
    return FileResponse(f"./img_data/{uuid}/gif/{uuid}.gif")

@app.get("/images/uuid/{uuid}/image/{index}")
def search_name(uuid: str, index:str):
    return FileResponse(f"./img_data/{uuid}/img/{index}.png")




class PortfolioData(BaseModel):
    userId: int
    shoeTitle: str
    shoeSize: float


@app.post("/user/addToPortfolio")
async def add_to_portfolio(data: PortfolioData):
    with sqlite3.connect(DATABASE_PATH) as conn:
        shoe_id_image = conn.cursor().execute("SELECT uuid,imageUrl FROM shoes WHERE title = ?", (data.shoeTitle,)).fetchone()

        if not shoe_id_image:
            raise HTTPException(400, "Shoe not found")

        conn.cursor().execute(
            "INSERT INTO portfolios (user_id, shoe_id, shoe_size) VALUES (?, ?, ?)",
            (data.userId, shoe_id_image[0], data.shoeSize),
        )
        conn.commit()

        download_first_image(shoe_id_image[1],shoe_id_image[0]) # Ensure we always have first image for showing in collection
        gif_process = Process(target=make_gif,args=(shoe_id_image[1],shoe_id_image[0]))
        gif_process.start()
        

    return {"status": "success", "message": "Shoe added to portfolio successfully!"}


@app.delete("/user/{user_id}/portfolio/{urlKey}")
async def delete_from_portfolio(user_id: int, urlKey: str):
    with sqlite3.connect(DATABASE_PATH) as conn:
        shoe = conn.cursor().execute("SELECT uuid FROM shoes WHERE urlKey = ?", (urlKey,)).fetchone()

        if not shoe:
            raise HTTPException(404, "Shoe not found")

        deleted_rows = conn.cursor().execute(
            "DELETE FROM portfolios WHERE user_id = ? AND shoe_id = ?",
            (user_id, shoe[0])
        ).rowcount
        conn.commit()

        if deleted_rows == 0:
            raise HTTPException(404, "Entry not found in portfolio")

    return {"status": "success", "message": "Shoe removed from portfolio successfully!"}

