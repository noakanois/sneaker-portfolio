from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from api.routes.portfolio import router_portfolio
from api.routes.search import router_search
from api.routes.user import router_user

import sqlite3
from api.db_utils import execute_sql, table_empty


app = FastAPI()
app.include_router(router_portfolio)
app.include_router(router_search)
app.include_router(router_user)

app.mount(
    "/static", StaticFiles(directory="../sneaker-frontend/build/static"), name="static"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get("/")
def serve_root_files():
    return FileResponse("../sneaker-frontend/build/index.html")


@app.get("/manifest.json")
def serve_manifest():
    return FileResponse("../sneaker-frontend/build/manifest.json")


@app.get("/favicon.ico")
def serve_favicon():
    return FileResponse("../sneaker-frontend/build/favicon.ico")


@app.get("/logo192.png")
def serve_logo():
    return FileResponse("../sneaker-frontend/build/logo192.png")


@app.exception_handler(sqlite3.DatabaseError)
async def database_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"message": "An error occurred with the database operation."},
    )
