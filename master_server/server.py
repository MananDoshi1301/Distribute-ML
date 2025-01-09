import uuid
from flask import Flask, request, jsonify
from rq import Queue
from app_configure import create_app
from app.queue import RedisQueue
from worker.worker import execute_model

server: Flask = create_app()

# setup config

# Initialize redis


# final_data= {
#     'data': {
#         'filenames': [
#             ('data_chunk_1.csv', '143e2b7b-8129-4336-8141-8a0fc1881259-data_chunk_1.csv'), 
#             ('data_chunk_2.csv', '2c1310ed-18d2-4a01-980f-405e8765e592-data_chunk_2.csv')
#         ], 
#         'partitions': 2
#     }, 
#     'record_id': 'e4ca6707-4e80-4fbc-acdf-b607d58666e0'
# }


@server.route("/tasks", methods=["POST"])
def process_task():
    data = request.get_json()          
    if not data: return jsonify({"error": "Missing data"}), 400

    data_dict = data['data']
    record_id = data['record_id']

    rq_client: Queue = RedisQueue().get_training_queue()

    # Push tasks in queue
    for file_tuple in data_dict['filenames']:        
        data_params: dict = {
            'data': file_tuple,
            'record_id': record_id
        }
        job = rq_client.enqueue(execute_model, data_params)
        

    return jsonify({"message": "Route sucess"}), 200

if __name__ == "__main__":
    PORT = 5002
    server.run(debug=True, port=PORT)