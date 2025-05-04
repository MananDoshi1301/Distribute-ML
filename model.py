import torch
import torch.nn as nn
import torch.optim as optim
import os, uuid
import json
import argparse
import pandas as pd
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

class LogisticRegressionModel(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.linear = nn.Linear(input_dim, 1)

    def forward(self, x):
        return torch.sigmoid(self.linear(x))

# Worker
def compute_gradients(model, data, target, output_path="/app/results/grads.json", worker_id=uuid.uuid4(), result_filename = f"res-random-{uuid.uuid4()}.json"):
    criterion = nn.BCELoss()
    output = model(data)
    loss = criterion(output, target)
    loss.backward()    

    grads_list = []
    for name, param in model.named_parameters():
        if param.grad is not None:
            layer, param_type = name.split(".")  # 'linear.weight' → 'linear', 'weight'
            grads_list.append({
                "layer": layer,
                "type": param_type,
                "values": param.grad.detach().cpu().numpy().tolist()
            })

    results_dir = output_path
    results_path = os.path.join(results_dir, result_filename)
    os.makedirs(results_dir, exist_ok=True)

    # os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print("Param computation complete. Writing file to volume at:", results_path)
    with open(results_path, 'w') as f:
        json.dump(grads_list, f)

    return grads_list

def evaluate_model(model, X, y):
    model.eval()
    X_tensor = torch.tensor(X, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.float32)

    with torch.no_grad():
        outputs = model(X_tensor)
        preds = (outputs > 0.5).float()

    y_true = y_tensor.numpy()
    y_pred = preds.numpy()

    print("Accuracy:", accuracy_score(y_true, y_pred))
    print("Precision:", precision_score(y_true, y_pred))
    print("Recall:", recall_score(y_true, y_pred))
    print("F1 Score:", f1_score(y_true, y_pred))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()    
    parser.add_argument("--output_path", type=str, default="/app/results/grads.json")
    parser.add_argument("--worker_id", type=str, default=str(uuid.uuid4()))
    parser.add_argument("--result_filename", type=str, default=f"res-random-{uuid.uuid4()}.json")
    parser.add_argument("--test_data", action='store_true')
    # parser.add_argument("--prepare_data", action='store_true', help="Prepare breast cancer dataset")
    args = parser.parse_args()    

    # Load CSV data
    print("Loading data")
    local_filename = "test.csv" if args.test_data else "data.csv"
    df = pd.read_csv(local_filename) 
    X = df.drop(columns=["target"]).values
    y = df["target"].values.reshape(-1, 1)

    # Normalize
    print("Normalizing data")
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    # Convert to tensors
    print("Converting data to tensors")
    X_tensor = torch.tensor(X, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.float32)

    print("Extracting params")
    updated_params = None
    if os.path.exists("latest_params.json"):
        with open("latest_params.json", "r") as f:
            updated_params = json.load(f)
    else:
        print("No params found!")
        updated_params = None

    print("Creating Model")
    model = LogisticRegressionModel(input_dim=X.shape[1])
    
    print("Loading params")
    if updated_params:
        with torch.no_grad():
            model.linear.weight.copy_(torch.tensor(updated_params["linear"]["weight"]))
            model.linear.bias.copy_(torch.tensor(updated_params["linear"]["bias"]))
            print("Adding params manually complete!")
    
    if args.test_data == True:
        print("Evaluating model on test data inside container...")
        evaluate_model(model, X, y)
    else:        
        print("Computing params")
        compute_gradients(model, X_tensor, y_tensor, output_path=args.output_path, worker_id=args.worker_id, result_filename=args.result_filename)