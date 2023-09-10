import sqlite3

conn = sqlite3.connect("../../shoes.db")

QUERY_UPDATE_PORTFOLIO = """
UPDATE portfolios SET shoe_id = (
    SELECT shoes.uuid 
    FROM shoes
    JOIN shoes_temp ON shoes_temp.id = portfolios.shoe_id
    WHERE shoes_temp.title = shoes.title AND shoes_temp.urlKey = shoes.urlKey
)
WHERE EXISTS (
    SELECT 1 
    FROM shoes
    JOIN shoes_temp ON shoes_temp.id = portfolios.shoe_id
    WHERE shoes_temp.title = shoes.title AND shoes_temp.urlKey = shoes.urlKey
);
"""

QUERY_RENAME_SHOE_ID = "Alter table portfolios RENAME COLUMN shoe_id TO shoe_uuid;"

conn.cursor().execute(QUERY_UPDATE_PORTFOLIO)
conn.cursor().execute(QUERY_RENAME_SHOE_ID)
conn.commit()
conn.close()
