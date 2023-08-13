from fastapi import FastAPI
import sqlite3
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException
from starlette.responses import Response
from fastapi.staticfiles import StaticFiles
from main import get_angle_images_from_original_image, make_gif
import threading

app = FastAPI()

DATABASE_PATH = "test.db"
conn = sqlite3.connect(DATABASE_PATH)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust this in production!
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
    
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT stylecode, image FROM shoes")
        results = cursor.fetchall()
        
    
    threads = []


    def process_shoe(style_code, image_url):
        get_angle_images_from_original_image(image_url, style_code)
        make_gif(image_url, style_code)


    for r in results:
        style_code, image_url = r
        t = threading.Thread(target=process_shoe, args=(style_code, image_url))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    
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
                s.name, s.stylecode, s.model, s.colorway, s.color, s.release_date,
                s.retail_price, s.extras, s.link, s.image, s.description
            FROM portfolios p
            JOIN shoes s ON p.shoe_id = s.id
            WHERE p.user_id = ?
        """, (user_id,))
        results = cursor.fetchall()
        return [{"shoe_size": r[0], "favorite": r[1], "name": r[2], "stylecode": r[3], "model": r[4], "colorway": r[5], "color": r[6], "release_date": r[7], "retail_price": r[8], "extras": r[9], "link": r[10], "image": r[11], "description": r[12]} for r in results]

    
    