from distributed_ml.master import Master

class DistributionConfig:
    # required
    MODEL_ENTRYPOINT = "model.py" 
    
    # required
    MODEL_DATA = "data.csv"
    
    # (default=requirements.txt)
    MODEL_REQUIREMENTS = "requirements.txt"
    
    # (default=10)
    TASK_PARTITION = 2
    
    # required
    TASK_OUTPUT = "weight"
    

if __name__ == "__main__":    
    master = Master()
    master.task_config(DistributionConfig)
    master.run()
    ...