import torch
import torch.nn as nn
import os, uuid, json, argparse, pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Model Definition
class ShallowDeepNN(nn.Module):
    def __init__(self, input_dim):
        super(ShallowDeepNN, self).__init__()
        self.layer1 = nn.Linear(input_dim, 64)
        self.relu = nn.ReLU()
        self.layer2 = nn.Linear(64, 32)
        self.layer3 = nn.Linear(32, 1)

    def forward(self, x):
        x = self.relu(self.layer1(x))
        x = self.relu(self.layer2(x))
        x = torch.sigmoid(self.layer3(x))
        return x

# Compute Gradients
def compute_gradients(model, data, target, output_path, worker_id, result_filename):
    model.train()
    criterion = nn.BCELoss()
    output = model(data)
    loss = criterion(output, target)
    loss.backward()

    grads_list = []
    for name, param in model.named_parameters():
        if param.grad is not None:
            layer, param_type = name.split(".")
            grads_list.append({
                "layer": layer,
                "type": param_type,
                "values": param.grad.detach().cpu().numpy().tolist()
            })

    os.makedirs(output_path, exist_ok=True)
    results_path = os.path.join(output_path, result_filename)
    with open(results_path, 'w') as f:
        json.dump(grads_list, f)
    print(f"[{worker_id}] Gradients written to {results_path}")
    return grads_list

# Evaluate Model
def evaluate_model(model, X, y):
    model.eval()
    with torch.no_grad():
        outputs = model(torch.tensor(X, dtype=torch.float32))
        preds = (outputs > 0.5).float()

    y_true = y.reshape(-1)
    y_pred = preds.numpy().reshape(-1)

    print("Accuracy :", accuracy_score(y_true, y_pred))
    print("Precision:", precision_score(y_true, y_pred))
    print("Recall   :", recall_score(y_true, y_pred))
    print("F1 Score :", f1_score(y_true, y_pred))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_path", type=str, default="/app/results/")
    parser.add_argument("--worker_id", type=str, default=str(uuid.uuid4()))
    parser.add_argument("--result_filename", type=str, default=f"res-{uuid.uuid4()}.json")
    parser.add_argument("--test_data", action='store_true')
    args = parser.parse_args()

    # Load data
    filename = "test.csv" if args.test_data else "data.csv"
    df = pd.read_csv(filename).dropna()
    print(df.columns)
    df["y"] = df["y"].map({"yes": 1, "no": 0})

    categorical_cols = ["job", "marital", "education", "default", "housing", "loan",
                    "contact", "month", "day_of_week", "poutcome"]
    df_encoded = pd.get_dummies(df, columns=categorical_cols)

    # Select features (drop target column and possibly non-useful ones like 'duration')
    X = df_encoded.drop(columns=["y", "duration"])  # 'duration' is often excluded in real use
    y = df_encoded["y"].values.reshape(-1, 1)

    # Prepare features and target
    # X = df[["Feature1", "Feature2"]].values
    # y = df["Target"].values.reshape(-1, 1)

    # Normalize data
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    # Convert to tensors
    X_tensor = torch.tensor(X, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.float32)

    # Initialize model
    model = ShallowDeepNN(input_dim=X.shape[1])

    # Load parameters if available
    if os.path.exists("latest_params.json"):
        with open("latest_params.json", "r") as f:
            params = json.load(f)
        with torch.no_grad():
            model.layer1.weight.copy_(torch.tensor(params["layer1"]["weight"]))
            model.layer1.bias.copy_(torch.tensor(params["layer1"]["bias"]))
            model.layer2.weight.copy_(torch.tensor(params["layer2"]["weight"]))
            model.layer2.bias.copy_(torch.tensor(params["layer2"]["bias"]))
            model.layer3.weight.copy_(torch.tensor(params["layer3"]["weight"]))
            model.layer3.bias.copy_(torch.tensor(params["layer3"]["bias"]))
        print(f"[{args.worker_id}] Parameters loaded.")

    if args.test_data:
        print(f"[{args.worker_id}] Evaluating model on test data...")
        evaluate_model(model, X, y)
    else:
        print(f"[{args.worker_id}] Computing gradients...")
        compute_gradients(model, X_tensor, y_tensor, args.output_path, args.worker_id, args.result_filename)
