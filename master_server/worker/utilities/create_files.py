import os 
def create_files(requirement_txt: bytes, model_py: bytes, record_id: str, path: str):

    if isinstance(requirement_txt, bytes):
        requirement_txt = requirement_txt.decode('utf-8')
    if isinstance(model_py, bytes):
        model_py = model_py.decode('utf-8')

    req_filename = os.path.join(path, f"requirements-{record_id}.txt")
    model_filename = os.path.join(path, f"model-{record_id}.py")

    with open(req_filename, "w") as req_file:
        req_file.write(requirement_txt.strip())

    with open(model_filename, "w") as model_file:
        model_file.write(model_py.strip())