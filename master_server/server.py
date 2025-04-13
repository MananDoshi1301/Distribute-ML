import uuid
from flask import Flask, request, jsonify
from rq import Queue
from app_configure import create_app
from app.queue import RedisQueue
from app.optimizer import run_optimizer
from worker.worker import execute_model
from worker.decorators import return_response
from app.sql_job_manager import record_job, worker_task_complete

server: Flask = create_app()

# setup config

# Initialize redis


# final_data= {
#     'data': {
#         "original_filename": "data.csv"
#         'filenames': [
#             ('data_chunk_1.csv', '143e2b7b-8129-4336-8141-8a0fc1881259-data_chunk_1.csv'),
#             ('data_chunk_2.csv', '2c1310ed-18d2-4a01-980f-405e8765e592-data_chunk_2.csv')
#         ],
#         'partitions': 2
#     },
#     'record_id': 'e4ca6707-4e80-4fbc-acdf-b607d58666e0'
# }


@server.route("/tasks", methods=["POST"])
@return_response
def process_task():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing data"}), 400

    err_res = {"error": ""}

    data_dict = data['data']
    data_filename = data_dict["original_filename"]
    record_id = data['record_id']

    # Task_id
    task_id = str(uuid.uuid4())

    #  Getting client
    try:
        rq_client: Queue = RedisQueue().get_training_queue()
    except Exception as e:
        err_res["error"] = "Error setting queue"
        print(e)
        return err_res, 400

    # Push tasks in queue
    job_list = []
    for file_tuple in data_dict['filenames']:
        worker_id = uuid.uuid4()
        data_params: dict = {
            "data": file_tuple,
            "data_filename": data_filename,
            "record_id": record_id,
            "task_id": task_id,
            "worker_id": worker_id
        }
        try:
            job = rq_client.enqueue(execute_model, data_params)
            job_list.append(str(worker_id))
        except Exception as e:
            print(e)
            err_res["Error enqueuing tasks"]
            return err_res, 400

    # SQL record for the task beginning
    sql_record_params = {
        "record_id": record_id,
        "task_id": task_id,
        "num_partitions": data_dict["partitions"],
        "expected_workers": data_dict["partitions"],
        "completed_workers": 0,
        "status": "in_progress"
    }
    record_job(sql_record_params)

    res = {
        "message": "Task submited successfully",
        "record_id": record_id,
        "job_list": job_list
    }

    return res, 200


@server.route("/optimize", methods=["POST"])
@return_response
def optimize_gradient():
    data = request.get_json()
    if not data:
        return {"error": "Missing data"}, 400
    
    """
    {
        'data': ['data_chunk_2.csv', '95293ee7-70c9-4449-8197-471cfbfcd323-data_chunk_2.csv'], 
        'data_filename': './data.csv', 
        'record_id': '44a3d781-8949-4364-88b8-160e7b1fbae0', 
        'task_id': '547fb1b4-421b-4e2b-87aa-70089e2e39b8',
        'worker_id': '0eb81264-3adc-4d75-89ac-41617fee789a', 
        'results': {
            'dir': './task_data/results-44a3d781-8949-4364-88b8-160e7b1fbae0', 
            'filenames': 'res-0eb81264-3adc-4d75-89ac-41617fee789a.json', 
            'iteration': 1
        }
    }
    """
    record_id = data["record_id"]
    response = worker_task_complete(record_id=record_id)

    if response["task_completion"] == False:    
        return {"data": data}, 200
    else:
        package = {
            "record_id": record_id
        }
        print("Running Optimizer...!")
        run_optimizer(data_package=package)
    return {"data": data}, 200

if __name__ == "__main__":
    PORT = 5002
    server.run(debug=True, port=PORT)
