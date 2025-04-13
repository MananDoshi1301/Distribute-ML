from app.sql_job_manager import get_optimizer_data
import json

"""
Data Package:
{
    "linear": {
        "weight": [[...], [...], ...],
        "bias": [[...], [...], ...]
    }
}
"""

class Optimizer:
    def __init__(self, data_package):
        self.record_id = data_package["record_id"]
        self.results_data = []
        ...

    def aggregate_gradients(self):
        ...

    def gather_data(self):
        # Gather from model_training.training_records.sql. 
        response = get_optimizer_data(record_id=self.record_id)        
        for data in response["data"]:
            decoded_data = json.loads(data)
            self.results_data.append(decoded_data[0])
        
        # print(self.results_data)        
        """[
            {'layer': 'linear', 'type': 'weight', 'values': [[-0.043297260999679565, 0.061524711549282074, -0.08264651149511337, 0.1086183488368988, 0.062237538397312164, -0.03615410253405571, -0.14033079147338867, 0.04552251845598221]]},
            {'layer': 'linear', 'type': 'weight', 'values': [[-0.0016996811609715223, 0.017420487478375435, -0.04972494766116142, -0.07247702777385712, -0.038829199969768524, -0.03721068426966667, 0.05483487993478775, -0.045384809374809265]]}
        ]"""

def run_optimizer(data_package: dict):
    optimizer = Optimizer(data_package)    
    optimizer.gather_data()    
    optimizer.aggregate_gradients()
    
if __name__ == "__main__":
    # run_optimizer(data_package=)
    ...