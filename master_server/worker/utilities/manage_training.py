import os, json

def begin_training(params: dict, docker_client, print_process):
    
    task_data_path = params['task_data_path']
    record_id = params['record_id']
    data_filename = params['data_filename']
    original_datafilename = params['original_datafilename']

    requirements_path = os.path.join(task_data_path, f"requirements-{record_id}.txt")
    model_path = os.path.join(task_data_path, f"model-{record_id}.py")
    data_path = os.path.join(task_data_path, data_filename)
    results_dir = os.path.join(task_data_path, f"results-{record_id}")    

    # Container paths
    container_app_path = "/app"
    container_requirements_path = f"{container_app_path}/requirements.txt"
    container_model_path = f"{container_app_path}/model.py"
    container_data_path = f"{container_app_path}/{original_datafilename}"
    # container_results_path = f"{container_app_path}/results.json"

    try:                             
        command_list: list[str] = [
            'ls',
            'python -m venv /app/.venv',
            'source /app/.venv/bin/activate',
            f"pip install -r {container_requirements_path} > /dev/null 2>&1",
            f"python {container_model_path}"
        ]
        command = f"/bin/bash -c '{' && '.join(command_list)}'"
        container = docker_client.containers.run(
            "ml-base:latest",  
            command=command,
            volumes={
                os.path.abspath(requirements_path): {"bind": container_requirements_path, "mode": "ro"},  # requirements.txt
                os.path.abspath(model_path): {"bind": container_model_path, "mode": "ro"},  # model.py
                os.path.abspath(data_path): {"bind": container_data_path, "mode": "ro"},  # data file
            },
            working_dir=container_app_path,  # Set working directory in the container
            detach=True,                
        )

        result = container.wait()
        logs = container.logs()       
        id = container.id 
        results_path = os.path.join(results_dir, f"res-{id}.json")
        os.makedirs(results_dir, exist_ok=True)
        with open(results_path, 'w') as f:
            results_data = {
                'logs': logs.decode('utf-8'),
                'result': result
            }
            json.dump(results_data, f)

        container.remove()
        print_process("Model Training Completion")
        return result, logs
    except Exception as e:
        print(f"Error while running container: {e}")
        raise