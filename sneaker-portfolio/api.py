from fastapi import FastAPI
import sqlite3
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException
from starlette.responses import Response
from fastapi.staticfiles import StaticFiles
from main import get_angle_images_from_original_image, make_gif
import datetime
from scrape import get_search_json
app = FastAPI()

DATABASE_PATH = "test.db"
conn = sqlite3.connect(DATABASE_PATH)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://0f8b-91-2-255-136.ngrok-free.app", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/data", StaticFiles(directory="data"), name="data")

@app.get("/")
async def root():
    return {"message": "Hello World"}


def execute_sql_file(file_path):
    with open(file_path, "r") as file:
        sql = file.read()
        cursor = conn.cursor()
        cursor.executescript(sql)
        conn.commit()

def is_table_empty(table_name):
    query = f"SELECT COUNT(*) FROM {table_name}"
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()
    row_count = cursor.fetchone()[0]
    return row_count == 0
               
@app.on_event("startup")
async def startup_db():
    sql_files = ["db_model/schema/users.sql", "db_model/schema/portfolios.sql", "db_model/schema/shoes.sql", "db_model/schema/users.sql"] 
    
    for sql_file in sql_files:
        execute_sql_file(sql_file)
        
    run_if_empty_files = ["db_model/data/user_data.sql", "db_model/data/shoe_data.sql", "db_model/data/portfolio_data.sql"]
    tables = ["users", "shoes", "portfolios"]
    
    for sql_file, table_name in zip(run_if_empty_files, tables):
        if is_table_empty(table_name):
            execute_sql_file(sql_file)
    
    # with sqlite3.connect(DATABASE_PATH) as conn:
    #     cursor = conn.cursor()
    #     cursor.execute("SELECT stylecode, image FROM shoes")
    #     results = cursor.fetchall()
        
    
    # threads = []

    # def process_shoe(style_code, image_url):
    #     get_angle_images_from_original_image(image_url, style_code)
    #     make_gif(image_url, style_code)


    # for r in results:
    #     style_code, image_url = r
    #     t = threading.Thread(target=process_shoe, args=(style_code, image_url))
    #     threads.append(t)
    #     t.start()
        
    # for t in threads:
    #     t.join()
        
    
@app.get("/users")
async def get_users():
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM users")
        results = cursor.fetchall()
        return [{"id": r[0], "name": r[1]} for r in results]

@app.get("/user/{user_id}/portfolio")
async def get_user_portfolio(user_id: int):
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                p.shoe_size, p.favorite,
                s.name, s.title, s.model, s.brand, s.urlKey,
                s.thumbUrl, s.smallImageUrl, s.imageUrl,
                s.description, s.retail_price, s.release_date,
                s.created_at
            FROM portfolios p
            JOIN shoes s ON p.shoe_id = s.id
            WHERE p.user_id = ?
        """, (user_id,))
        results = cursor.fetchall()
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
                "created_at": r[13]
            }
            for r in results
        ]

@app.get("/search/name/{name}")
def get_name_json(name: str):
    search_results = get_search_json(name)  # Assuming this function retrieves search results

    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()

        # Insert the search results into the database
        for result in search_results:
            cursor.execute("""
                INSERT OR REPLACE INTO shoes (name, title, model, brand, urlKey, thumbUrl, smallImageUrl, imageUrl,
                                  description, retail_price, release_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result["name"],
                result["title"],
                result["model"],
                result["brand"],
                result["urlKey"],
                result["thumbUrl"],
                result["smallImageUrl"],
                result["imageUrl"],
                result["description"],
                result["retailPrice"],
                result["releaseDate"],
                datetime.datetime.now()
            ))

        conn.commit()  # Commit the changes to the database

    return search_results

from pydantic import BaseModel

class AddShoeToPortfolio(BaseModel):
    userId: int
    shoeTitle: str
    shoeSize: float
    
@app.post("/user/addToPortfolio")
async def add_shoe_to_portfolio(shoe_data: AddShoeToPortfolio):
    user_id = shoe_data.userId
    shoe_title = shoe_data.shoeTitle
    shoe_size = shoe_data.shoeSize

    # Find the shoe ID based on the shoe title (assuming title is unique for simplification)
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM shoes WHERE title = ?", (shoe_title,))
        shoe_id = cursor.fetchone()

        # If shoe is not found, return an error
        if not shoe_id:
            raise HTTPException(status_code=400, detail="Shoe not found")

        # Add to the portfolio
        cursor.execute("INSERT INTO portfolios (user_id, shoe_id, shoe_size) VALUES (?, ?, ?)",
                       (user_id, shoe_id[0], shoe_size))
        conn.commit()

    return {"status": "success", "message": "Shoe added to portfolio successfully!"}

@app.delete("/user/{user_id}/portfolio/{urlKey}")
async def delete_shoe_from_portfolio(user_id: int, urlKey: str):
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM shoes WHERE urlKey = ?", (urlKey,))
        shoe = cursor.fetchone()
        
        if not shoe:
            raise HTTPException(status_code=404, detail="Shoe not found")

        shoe_id = shoe[0]
        
        cursor.execute("""
            DELETE FROM portfolios WHERE user_id = ? AND shoe_id = ?
        """, (user_id, shoe_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Entry not found in portfolio")

    return {"status": "success", "message": "Shoe removed from portfolio successfully!"}
