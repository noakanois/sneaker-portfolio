CREATE TABLE IF NOT EXISTS portfolios (
    "user_id"  INTEGER NOT NULL,
    "shoe_id"  INTEGER NOT NULL,
    "shoe_size"  TEXT NOT NULL,
    "favorite" BOOLEAN NOT NULL DEFAULT FALSE,
    "created_at" TIMESTAMP, 
    "updated_at" TIMESTAMP
)