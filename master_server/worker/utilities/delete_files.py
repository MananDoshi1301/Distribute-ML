import os

def delete_files(record_id: str, path: str):

    req_filename = os.path.join(path, f"requirements-{record_id}.txt")
    model_filename = os.path.join(path, f"model-{record_id}.py")

    if os.path.exists(req_filename): os.remove(req_filename)
    if os.path.exists(model_filename): os.remove(model_filename)    