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

-- dict = {
--     "record_id": record_id,
--     "task_id": task_id,
--     "num_partitions": 2,
--     "expected_workers": 2,
--     "completed_workers": 0,
--     "status": "in_progress"
-- }