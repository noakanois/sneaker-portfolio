INSERT OR IGNORE INTO users ("name", "created_at", "updated_at")
SELECT 'Noah', datetime('now'), datetime('now')
WHERE NOT EXISTS (SELECT 1 FROM users WHERE "name" = 'Noah');

INSERT OR IGNORE INTO users ("name", "created_at", "updated_at")
SELECT 'Daniel', datetime('now'), datetime('now')
WHERE NOT EXISTS (SELECT 1 FROM users WHERE "name" = 'Daniel');