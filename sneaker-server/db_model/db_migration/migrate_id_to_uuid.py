import sqlite3
import pandas as pd
import uuid

QUERY_SHOES_2 = """
    CREATE TABLE IF NOT EXISTS shoes2 (
        "uuid" TEXT UNIQUE PRIMARY KEY,
        "name" TEXT,
        "title" TEXT,
        "model" TEXT,
        "brand" TEXT,
        "urlKey" TEXT,
        "thumbUrl" TEXT,
        "smallImageUrl" TEXT,
        "imageUrl" TEXT,
        "description" TEXT,
        "retail_price" TEXT,
        "release_date" TIMESTAMP,
        "created_at" TIMESTAMP
    );
"""

conn = sqlite3.connect("../../shoes.db")
df = pd.read_sql_query("SELECT * FROM shoes", conn)
conn.cursor().execute(QUERY_SHOES_2)
conn.commit()

df["id"] = df.apply(
    lambda row: str(uuid.uuid5(uuid.NAMESPACE_X500, f"{row['title']}{row['urlKey']}")),
    axis=1,
)
df = df.rename(columns={"id": "uuid"})
df = df.drop_duplicates(subset="uuid")
df.to_sql("shoes2", conn, if_exists="append", index=False)

QUERY_SHOES_TEMP = "ALTER TABLE shoes RENAME TO shoes_temp"
QUERY_SHOES2_SHOES = "ALTER TABLE shoes2 RENAME TO shoes"

conn.cursor().execute(QUERY_SHOES_TEMP)
conn.cursor().execute(QUERY_SHOES2_SHOES)
conn.commit()
conn.close()
