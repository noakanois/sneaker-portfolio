import sqlite3

conn = sqlite3.connect("../../test.db")

QUERY_INSERT_USER = """
    INSERT OR IGNORE INTO users ("name", "created_at", "updated_at")
    SELECT 'Pipicu', datetime('now'), datetime('now')
    WHERE NOT EXISTS (SELECT 1 FROM users WHERE "name" = 'Pipicu');
"""

QUERY_RENAME_SHOE_ID = "Alter table portfolios RENAME COLUMN shoe_id TO shoe_uuid;"

conn.cursor().execute(QUERY_INSERT_USER)

conn.commit()
conn.close()
