CREATE DATABASE bitcoin_assets CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE bitcoin_assets.transaction (
    id INT(7) PRIMARY KEY,
    name VARCHAR(64) NOT NULL
);
INSERT INTO bitcoin_assets.transaction VALUES
    (1, 'Spanish'),
    (2, 'German'),
    (3, 'English');
