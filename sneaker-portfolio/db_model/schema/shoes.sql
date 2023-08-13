CREATE TABLE IF NOT EXISTS shoes (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
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