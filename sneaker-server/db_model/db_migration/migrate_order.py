import sqlite3

conn = sqlite3.connect("../../test.db")

QUERY_ADD_GRID_ORDER = """
    ALTER TABLE portfolios ADD order_position INTEGER;
"""

conn.cursor().execute(QUERY_ADD_GRID_ORDER)
print(conn.cursor().fetchall())
conn.commit()
conn.close()
