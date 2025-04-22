from distribute_ml.master import Master
# from torch.nn import optim
from torch import optim

class DistributionConfig:
    # required
    MODEL_ENTRYPOINT = "./model.py" 
    
    # required
    MODEL_DATA = "./data.csv"
    
    # (default=requirements.txt)
    MODEL_REQUIREMENTS = "./requirements.txt"
    
    # (default=10)
    TASK_PARTITION = 2
    
    # required
    TASK_OUTPUT = "weight"

    # required
    OPTIMIZER = optim.SGD
    
    # required
    OPTIMIZER_PARAMS = {
        "lr": 0.01,
        "momentum": 0.9
    }
    
    # required
    INITIAL_PARAMS = {
        "linear": {
            "weight": [[0.0 for _ in range(8)]],  
            "bias": [0.0]
        }
    }

    TOTAL_ITERATIONS = 15

    TRAIN_SPLIT = 0.7
    TEST_SPLIT = 0.15
    VALIDATION_SPLIT = 0.15