CREATE DATABASE IF NOT EXISTS oto_ads CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE oto_ads;

CREATE TABLE IF NOT EXISTS ads (
    ad_id BIGINT PRIMARY KEY,
    list_id BIGINT,
    list_time BIGINT,
    state VARCHAR(50),
    type CHAR(1),
    account_name TEXT,
    region INT,
    category INT,
    company_ad BOOLEAN,
    subject TEXT,
    body TEXT,
    price BIGINT,
    image TEXT,
    account_id BIGINT,
    shop_alias VARCHAR(255),
    status VARCHAR(50),
    carbrand INT,
    carmodel INT,
    carorigin INT,
    carseats INT,
    fuel INT,
    gearbox INT,
    mfdate INT,
    mileage FLOAT,
    mileage_v2 FLOAT,
    area INT,
    condition_ad INT,
    longitude DOUBLE,
    latitude DOUBLE,
    contain_videos BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ad_images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ad_id BIGINT,
    image_url TEXT,
    FOREIGN KEY (ad_id) REFERENCES ads(ad_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ad_videos (
    id VARCHAR(64) PRIMARY KEY,
    ad_id BIGINT,
    thumbnail TEXT,
    url TEXT,
    gif_url TEXT,
    FOREIGN KEY (ad_id) REFERENCES ads(ad_id) ON DELETE CASCADE
);
