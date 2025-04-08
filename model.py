import torch
import torch.nn as nn
import torch.optim as optim
import os, uuid
import json
import argparse
import pandas as pd
from sklearn.preprocessing import StandardScaler

class LogisticRegressionModel(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.linear = nn.Linear(input_dim, 1)

    def forward(self, x):
        return torch.sigmoid(self.linear(x))

# Worker
def compute_gradients(model, data, target, output_path="/app/results/grads.json", worker_id=uuid.uuid4()):
    criterion = nn.BCELoss()
    output = model(data)
    loss = criterion(output, target)
    loss.backward()

    # grads_dict = {
    #     name: param.grad.detach().cpu().numpy().tolist()
    #     for name, param in model.named_parameters()
    #     if param.grad is not None
    # }

    # grads_dict = {}
    # for name, param in model.named_parameters():
    #     if "weight" in name:
    #         grads_dict["weight"] = param.grad.detach().cpu().numpy().tolist()
    #     elif "bias" in name:
    #         grads_dict["bias"] = param.grad.detach().cpu().numpy().tolist()

    grads_list = []
    for name, param in model.named_parameters():
        if param.grad is not None:
            layer, param_type = name.split(".")  # 'linear.weight' → 'linear', 'weight'
            grads_list.append({
                "layer": layer,
                "type": param_type,
                "values": param.grad.detach().cpu().numpy().tolist()
            })

    # results_path = os.path.join(results_dir, f"res-{id}.json")
    # os.makedirs(results_dir, exist_ok=True)
    # with open(results_path, 'w') as f:
    #     results_data = {
    #         'logs': logs.decode('utf-8'),
    #         'result': result
    #     }
    #     json.dump(results_data, f)

    results_dir = output_path
    results_path = os.path.join(results_dir, f"res-{worker_id}.json")
    os.makedirs(results_dir, exist_ok=True)

    # os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(results_path, 'w') as f:
        json.dump(grads_list, f)

    return grads_list

if __name__ == "__main__":
    parser = argparse.ArgumentParser()    
    parser.add_argument("--output_path", type=str, default="/app/results/grads.json")
    parser.add_argument("--worker_id", type=str, default=uuid.uuid4())
    args = parser.parse_args()

    # Load CSV data
    df = pd.read_csv("data.csv")
    X = df.drop(columns=["label_encoded"]).values
    y = df["label_encoded"].values.reshape(-1, 1)

    # Normalize
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    # Convert to tensors
    X_tensor = torch.tensor(X, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.float32)

    model = LogisticRegressionModel(input_dim=X.shape[1])
    compute_gradients(model, X_tensor, y_tensor, output_path=args.output_path, worker_id = args.worker_id)