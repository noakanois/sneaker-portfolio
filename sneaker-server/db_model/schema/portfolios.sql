CREATE TABLE IF NOT EXISTS portfolios (
    "user_id"  INTEGER NOT NULL,
    "shoe_uuid"  INTEGER NOT NULL,
    "shoe_size"  TEXT NOT NULL,
    "order_position" INTEGER,
    "favorite" BOOLEAN NOT NULL DEFAULT FALSE,
    "created_at" TIMESTAMP, 
    "updated_at" TIMESTAMP
)