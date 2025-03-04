from distribute_ml.master import Master
from conf import DistributionConfig

if __name__ == "__main__":    
    master = Master()
    master.set_config(DistributionConfig)
    master.train()    