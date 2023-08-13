CREATE TABLE IF NOT EXISTS shoes (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "name" TEXT NOT NULL,
    "model" TEXT NOT NULL,
    "brand" TEXT NOT NULL,
    "urlKey" TEXT NOT NULL,
    "thumbUrl" TEXT NOT NULL,
    "smallImageUrl" TEXT NOT NULL,
    "imageUrl" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "retail_price" TEXT NOT NULL,
    "release_date" TIMESTAMP NOT NULL,
    "created_at" TIMESTAMP
);