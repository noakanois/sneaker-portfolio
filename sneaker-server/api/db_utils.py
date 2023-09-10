import sqlite3

DATABASE_PATH = "shoes.db"


def execute_sql(file_path):
    with open(file_path, "r") as f, sqlite3.connect(DATABASE_PATH) as conn:
        conn.cursor().executescript(f.read())
        conn.commit()


def table_empty(table):
    with sqlite3.connect(DATABASE_PATH) as conn:
        row_count = conn.cursor().execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    return row_count == 0


def get_db():
    try:
        db = sqlite3.connect(DATABASE_PATH)
        yield db
    finally:
        db.close()
