import numpy as np
from collections import defaultdict
from app.sql_job_manager import get_optimizer_data, update_training_state, save_new_params, delete_old_transaction_records, get_iterations_info, get_reiteration_info

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
        self.data_aggregation = {}
        self.lr = data_package.get("lr", 0.01)
        self.old_params = data_package.get("initial_params", {})        


    def optimize(self):
        """self.data_aggregation = {
            'linear': {
                'weight': [
                    [[-0.015894798561930656, 0.014964492991566658, -0.10894323140382767, 0.04732732102274895, -0.05168985575437546, -0.011154105886816978, -0.09705221652984619, -0.026199696585536003]], 
                    [[-0.05793697386980057, 0.002460323041304946, -0.030546939000487328, 0.052860986441373825, -0.049563560634851456, -0.03070954978466034, 0.039908211678266525, -0.07345663011074066]]
                ], 
                'bias': [[0.09387437999248505], [-0.012285656295716763]]
            }
        }"""
        # Implement optimizer

        updated_params = {}

        for layer_name, params in self.data_aggregation.items():
            updated_params[layer_name] = {}
            
            for param_type, gradients_list in params.items():
                avg_gradient = np.mean(gradients_list, axis=0)

                # If initial params not given, initialize with zeros
                if (
                    layer_name in self.old_params and 
                    param_type in self.old_params[layer_name]
                ):
                    old_param = np.array(self.old_params[layer_name][param_type])
                else:
                    # Create a zero array of the same shape as the gradient
                    old_param = np.zeros_like(avg_gradient)
                
                new_param = old_param - self.lr * avg_gradient
                updated_params[layer_name][param_type] = new_param.tolist()

        self.updated_params = updated_params
        print("UPDATED PARAMS:\n", updated_params)
        
    # def optimize(self):
    #     ...

    def aggregate_gradients(self):
                
        for arr in self.results_data:
            for object in arr:
                layer_name = object["layer"]
                _type = object["type"]
                values = object["values"]
                if layer_name not in self.data_aggregation: self.data_aggregation[layer_name] = {}
                if _type not in self.data_aggregation[layer_name]: self.data_aggregation[layer_name][_type] = []
                self.data_aggregation[layer_name][_type].append(values)

        """
        self.data_aggregation = {
            'linear': {
                'weight': [
                    [[-0.015894798561930656, 0.014964492991566658, -0.10894323140382767, 0.04732732102274895, -0.05168985575437546, -0.011154105886816978, -0.09705221652984619, -0.026199696585536003]], 
                    [[-0.05793697386980057, 0.002460323041304946, -0.030546939000487328, 0.052860986441373825, -0.049563560634851456, -0.03070954978466034, 0.039908211678266525, -0.07345663011074066]]
                ], 
                'bias': [[0.09387437999248505], [-0.012285656295716763]]
            }
        }
        """

    def gather_data(self):
        # Gather from model_training.training_records.sql. 
        response = get_optimizer_data(record_id=self.record_id) 
        update_response = update_training_state(record_id=self.record_id)
        self.results_data = response["data"]        
        
        """[
            [
                {
                    'layer': 'linear', 
                    'type': 'weight', 
                    'values': [
                        [0.02058419957756996, -0.07127335667610168, 0.04015723615884781, 0.07739932835102081, -0.04254637658596039, 0.048054538667201996, -0.0044463337399065495, -0.04846640303730965]
                    ]
                }, 
                {
                    'layer': 'linear', 
                    'type': 'bias', 
                    'values': [-0.10121934860944748]
                }
            ], 

            [
                {
                    'layer': 'linear', 
                    'type': 'weight', 
                    'values': [
                        [-0.015549459494650364, -0.015824604779481888, -0.10921275615692139, 0.016397273167967796, -0.029397018253803253, 0.00722794234752655, -0.07098878175020218, -0.06022842228412628]
                    ]
                }, 
                {
                    'layer': 'linear', 
                    'type': 'bias', 
                    'values': [0.05033407732844353]
                }
            ]
        ]"""

    def update_weights(self):
        try:
            response = save_new_params(record_id=self.record_id, params=self.updated_params)
            if response:
                print("New weights saved successfully!")
        except Exception as e:
            raise e      

    def delete_old_jobs(self):
        try:
            response = delete_old_transaction_records(record_id=self.record_id)
            if response:
                print("Old jobs deleted successfully!")
        except Exception as e:
            raise e 

    def iterations_data(self):
        try:
            response = get_iterations_info(record_id=self.record_id)
            if response["success"] == True:
                return response
        except Exception as e:
            raise e 
        
    def reiteration_data(self):
        try:
            response = get_reiteration_info(record_id=self.record_id)
            if response["success"] == True:
                return response
        except Exception as e:
            raise e 

def print_process(header: str):
    print(f"{'=' * 7}\t {header} \t{'=' * 7}")

def run_optimizer(data_package: dict):
    optimizer = Optimizer(data_package)    
    print_process("Optimizer begins...")
    print_process("Gathering Data")
    optimizer.gather_data()    
    print_process("Aggregating data")
    optimizer.aggregate_gradients()
    print_process("Optimizing data")
    optimizer.optimize()      
    print_process("Updating weights on db")
    optimizer.update_weights()
    print_process("Getting iterations info")
    response = optimizer.iterations_data()

    if response["more_iterations"] == True:
        print_process("Getting new iteration info")
        data_dict_response = optimizer.reiteration_data()
        data_dict = data_dict_response["data"]
        response["new_iteration_data_dict"] = data_dict
    else:
        response["new_iteration_data_dict"] = None
    # response["new_iteration_data_dict"] = None

    print_process("Deleting old recorded jobs")
    optimizer.delete_old_jobs()      
    print_process("Optimizer end!")

    # print("********** Response:", response)

    return response
    
if __name__ == "__main__":
    # run_optimizer(data_package=)
    ...