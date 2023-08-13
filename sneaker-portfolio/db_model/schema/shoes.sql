CREATE TABLE IF NOT EXISTS shoes (
    "id"  INTEGER PRIMARY KEY AUTOINCREMENT,
    "name" TEXT NOT NULL,
    "stylecode" TEXT NOT NULL,
    "model"   TEXT NOT NULL,
    "colorway" TEXT NOT NULL,
    "color" TEXT NOT NULL,
    "release_date" TIMESTAMP NOT NULL,
    "retail_price" TEXT NOT NULL,
    "extras" TEXT,
    "link" TEXT NOT NULL,
    "image" TEXT NOT NULL,
    "description" TEXT,
    "created_at" TIMESTAMP
)