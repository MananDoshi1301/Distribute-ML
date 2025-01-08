CREATE DATABASE IF NOT EXISTS model_files;

USE model_files;

CREATE TABLE IF NOT EXISTS models(
    id VARCHAR(36) PRIMARY KEY,
    filename VARCHAR(255),
    content LONGBLOB,
    upload_time DATETIME
);