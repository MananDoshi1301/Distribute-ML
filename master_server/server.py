import uuid
from flask import Flask, request, jsonify
from rq import Queue
from app_configure import create_app
from app.queue import RedisQueue
from app.optimizer import run_optimizer
from worker.worker import execute_model
from worker.decorators import return_response
from app.sql_job_manager import record_job, worker_task_complete, update_worker_on_new_iteration

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
#     'total_iterations': 10,
#     'record_id': 'e4ca6707-4e80-4fbc-acdf-b607d58666e0'
# }

err_res = {"error": ""}

# Getting rq client
def get_rq_client():
    try:
        rq_client: Queue = RedisQueue().get_training_queue()
        return True, rq_client, 200
    except Exception as e:
        err_res["error"] = "Error setting queue"
        print(e)
        return False, err_res, 400
    
def push_tasks(data_dict: dict) -> list:
    # data_dict = {
    #     'original_filename': './data.csv', 
    #     'filenames': [
    #         ['data_chunk_1.csv', '5d3a7010-9f87-45c8-b82a-bade79ad0e37-data_chunk_1.csv'], 
    #         ['data_chunk_2.csv', '085014c1-55d7-40eb-a4a4-8c5516008d2d-data_chunk_2.csv']
    #     ], 
    #     'partitions': 2, 
    #     'record_id': '80c69045-06a0-4d48-b506-118cc8be904d'
    # }

    #Filenames    
    response, rq_client, statuscode = get_rq_client()
    if statuscode == 400 or response == False: raise ValueError(f"No rq client found: {rq_client}")
    data_filename = data_dict["original_filename"]
    record_id = data_dict['record_id']
    task_id = str(uuid.uuid4())

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
    return job_list


@server.route("/tasks", methods=["POST"])
@return_response
def process_task():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing data"}), 400

    #  Getting client
    response, _, statuscode = get_rq_client()
    if response == False: return err_res, statuscode

    data_dict = data['data']
    record_id = data['record_id']
    data_dict["record_id"] = record_id
    # Task_id
    task_id = str(uuid.uuid4())
    total_iterations = data['total_iterations']



    # Push tasks in queue
    job_list = push_tasks(data_dict=data_dict)

    # SQL record for the task beginning
    sql_record_params = {
        "record_id": record_id,
        "task_id": task_id,
        "num_partitions": data_dict["partitions"],
        "expected_workers": data_dict["partitions"],
        "completed_workers": 0,
        "status": "in_progress",
        "total_iterations": total_iterations,
        "iterations_complete": 1
    }
    # Record job that begins -> sql request
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

        optimizer_response = run_optimizer(data_package=package)        
        data = optimizer_response["data"]
        
        # If iterations complete < total_iterations: run the task again
        if data["total_iterations"] > data["iterations_complete"]:                    
            data_dict = optimizer_response["new_iteration_data_dict"]
            print("Training again!")
            update_worker_on_new_iteration(record_id=record_id)
            _ = push_tasks(data_dict=data_dict)
        else:
            print("<********* Iterations Complete *********>")

    return {"data": data}, 200

if __name__ == "__main__":
    PORT = 5002
    server.run(debug=True, port=PORT)
