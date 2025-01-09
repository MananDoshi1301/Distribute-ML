class Models:
    def __init__(self, id, model_filename, model_content, requirements_filename, requirements_content, upload_time = None):
        self.id = id,
        self.model_filename = model_filename,
        self.model_content = model_content,
        self.requirements_filename = requirements_filename,
        self.requirements_content = requirements_content,
        self.upload_time = upload_time
    
    def get_dict(self) -> dict:
        data = {
            "id": self.id,
            "model_filename": self.model_filename,
            "model_content": self.model_content,
            "requirements_filename": self.requirements_filename,
            "requirements_content": self.requirements_content,
            "upload_time": self.upload_time
        }
        return data