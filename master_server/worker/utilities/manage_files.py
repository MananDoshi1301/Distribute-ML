import os, json
from typing import Any

class LocalFileManager:
    def __init__(self, requirement_txt: bytes, model_py: bytes, model_params: dict, record_id: str, path: str):
        self.requirement_content = requirement_txt
        self.model_content = model_py
        self.record_id = record_id
        self.model_params = model_params
        self.base_path = path        
    
    def write_file(self, file_path: str, file_content: Any):     
        try:   
            with open(file_path, "w") as req_file:
                req_file.write(file_content.strip())
        except Exception as e:
            raise e
        return True

    def create_model_file(self):
        
        if isinstance(self.model_content, bytes):
            model_py = self.model_content.decode('utf-8')

        model_filename = os.path.join(self.base_path, f"model-{self.record_id}.py")
        
        self.write_file(model_filename, model_py) 

    def create_requirement_file(self):
        
        if isinstance(self.requirement_content, bytes):
            requirement_txt = self.requirement_content.decode('utf-8')

        req_filename = os.path.join(self.base_path, f"requirements-{self.record_id}.txt")
        
        self.write_file(req_filename, requirement_txt)          

    def create_params_file(self):
        print("<------ Creating param files ------>")  
        print(self.model_params, type(self.model_params))      
        if isinstance(self.model_params, dict):
            model_params = json.dumps(self.model_params)            

        model_params_filename = os.path.join(self.base_path, f"latest_params-{self.record_id}.json")
        
        self.write_file(model_params_filename, model_params)
        print("<------ Param files creation complete! ------>")        

    def create_all_files(self):
        self.create_model_file()
        self.create_requirement_file()
        self.create_params_file()

    def delete_all_files(self):
        req_filename = os.path.join(self.base_path, f"requirements-{self.record_id}.txt")
        model_filename = os.path.join(self.base_path, f"model-{self.record_id}.py")
        model_params_filename = os.path.join(self.base_path, f"latest_params-{self.record_id}.json")
        if os.path.exists(req_filename): os.remove(req_filename)
        if os.path.exists(model_filename): os.remove(model_filename)    
        if os.path.exists(model_params_filename): os.remove(model_params_filename)      