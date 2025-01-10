from distribute_ml.master import Master
from conf import DistributionConfig

if __name__ == "__main__":    
    master = Master()
    master.task_config(DistributionConfig)
    master.train()    