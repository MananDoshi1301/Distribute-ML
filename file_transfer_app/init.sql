CREATE DATABASE IF NOT EXISTS model_files;

USE model_files;

CREATE TABLE IF NOT EXISTS models(
    id VARCHAR(36) PRIMARY KEY,
    model_filename VARCHAR(255),
    model_content LONGBLOB,
    requirements_filename VARCHAR(255),
    requirements_content LONGBLOB,
    upload_time DATETIME
);