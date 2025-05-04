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

CREATE DATABASE IF NOT EXISTS model_training;

USE model_training;

CREATE TABLE IF NOT EXISTS training_records(
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    record_id VARCHAR(255),
    task_id VARCHAR(255),
    worker_id VARCHAR(255),
    data_chunkname VARCHAR(255),
    data_sourcename VARCHAR(255), 
    results_filename VARCHAR(255),   
    results_content LONGBLOB,
    training_iteration INT
);

CREATE DATABASE IF NOT EXISTS model_training;

USE model_training;

CREATE TABLE IF NOT EXISTS master_training_records (
    id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    record_id VARCHAR(255) NOT NULL,
    task_id VARCHAR(255) NOT NULL,
    num_partitions INT NOT NULL,
    expected_workers INT NOT NULL,
    completed_workers INT DEFAULT 0,
    status ENUM('in_progress', 'ready_to_optimize', 'optimizing', 'done', 'failed') DEFAULT 'in_progress',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);