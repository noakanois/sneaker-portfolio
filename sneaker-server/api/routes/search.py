from fastapi import APIRouter
from ..utils.db_utils import DATABASE_PATH
from ..utils.scrape_utils import get_search_json
import sqlite3
import datetime
import uuid

router_search = APIRouter()

QUERY_INSERT_SHOE = """
    INSERT OR IGNORE
    INTO shoes 
        (
        uuid, name, title, model, brand, urlKey, thumbUrl, 
        smallImageUrl, imageUrl, description, retail_price, 
        release_date, created_at
        )
    VALUES 
        (
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
"""


@router_search.get("/search/name/{name}")
def search_name(name: str):
    with sqlite3.connect(DATABASE_PATH) as conn:
        results = get_search_json(name)
        for r in results:
            shoe_uuid = uuid.uuid5(uuid.NAMESPACE_X500, f"{r['title']}{r['urlKey']}")
            conn.cursor().execute(
                QUERY_INSERT_SHOE,
                (
                    str(shoe_uuid),
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
                ),
            )
        conn.commit()

    return results
