import sys
from .app.utilities.split_data import split_data

def hello():
    print("Hello From module!")


class Master:
    def __init__(self):
        self.task_params: dict = {}

    def task_config(self, config_cls: type):
        required_params = ["MODEL_ENTRYPOINT", "MODEL_DATA", "TASK_OUTPUT"]
        final_params = {
            "MODEL_ENTRYPOINT": "", "MODEL_DATA": "", "TASK_OUTPUT": "",
            "MODEL_REQUIREMENTS": "requirements.txt", "TASK_PARTITION": 10
        }
        
        all_configs = {k:v for k, v in vars(config_cls).items()}
        config_attrs = {k:v for k, v in all_configs.items() if not k.startswith("__")}
        
        # Checking for required params
        for param in required_params:
            if param not in config_attrs: 
                print(f"Missing required param: {param}")
                print("Exiting the program")
                sys.exit()

        # Setting overrided params
        for k, _ in final_params.items():
            if k in config_attrs: final_params[k] = config_attrs[k]

        print("Task config set successfully!")
        self.task_params = final_params

    def run(self):
        # Validate incoming code and data        

        # Split data file 
        filename, n_partitions = self.task_params['MODEL_DATA'], self.task_params['TASK_PARTITION']
        new_file_names: list[str] = split_data(filename, n_partitions)
        print(new_file_names)
            # push data to cloud            
            # Create a task. Push to sql db

        # Push tasks to queue
        ...