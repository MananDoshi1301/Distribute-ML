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


-- {
--     'data': ['data_chunk_2.csv', '95293ee7-70c9-4449-8197-471cfbfcd323-data_chunk_2.csv'], 
--     'data_filename': './data.csv', 
--     'record_id': '44a3d781-8949-4364-88b8-160e7b1fbae0', 
--     'task_id': '547fb1b4-421b-4e2b-87aa-70089e2e39b8',
--     'worker_id': '0eb81264-3adc-4d75-89ac-41617fee789a', 
--     'results': {
--         'dir': './task_data/results-44a3d781-8949-4364-88b8-160e7b1fbae0', 
--         'filenames': 'res-0eb81264-3adc-4d75-89ac-41617fee789a.json', 
--         'iteration': 1
--     }
-- }