# Unused file
import os, virtualenv, shutil

# Unused function (Upgraded to docker containers)
def create_venv(record_id: str, task_data_path: str) -> str:
    venv_path = f"/tmp/venv_{record_id}"
    print("---> Creating Virtual Env at:", venv_path)
    virtualenv.cli_run([venv_path])
    print("---> Creating Requirements Path")        
    requirements_path = os.path.join(task_data_path, f"requirements-{record_id}.txt")
    print("---> Starting virtual env and installing requirements")
    os.system(f"source {venv_path}/bin/activate && pip install -r {requirements_path}")        
    # Fresh fetch
    # os.system(f"source {venv_path}/bin/activate && pip install --no-cache-dir -r {requirements_path}")        
    print("*--- Virtual Environment Created Successfully ---*")
    return venv_path

# Unused function (Upgraded to docker containers)
def remove_venv(record_id: str):
    venv_path = f"/tmp/venv_{record_id}"
    if os.path.exists(venv_path):
        shutil.rmtree(venv_path)
        print(f"*--- Venv removed successfully:{venv_path} ---*")        