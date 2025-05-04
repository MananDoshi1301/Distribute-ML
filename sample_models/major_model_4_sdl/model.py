# # Import necessary libraries
# import numpy as np, argparse, pandas as pd, uuid
# from sklearn.datasets import make_moons
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import StandardScaler
# import tensorflow as tf, os, json
# from tensorflow.keras.models import Sequential
# from tensorflow.keras.layers import Dense
# from tensorflow.keras.optimizers import Adam


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()    
#     parser.add_argument("--output_path", type=str, default="/app/results/grads.json")
#     parser.add_argument("--worker_id", type=str, default=uuid.uuid4())
#     parser.add_argument("--result_filename", type=str, default=f"res-random-{uuid.uuid4()}.json")
#     parser.add_argument("--test_data", action='store_true')    
#     args = parser.parse_args()

#     # Load CSV data
#     print("Loading data")
#     local_filename = "test.csv" if args.test_data else "data.csv"
#     df = pd.read_csv(local_filename) 
#     df = df.dropna()

#     X = df.drop(columns=["Target"]).values
#     y = df["Target"].values.reshape(-1, 1)


#     # Split the dataset into training and test sets
#     # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

#     # Scale the features
#     scaler = StandardScaler()
#     if args.test_data == True:
#         X_scaled = scaler.transform(X)
#     else:
#         X_scaled = scaler.fit_transform(X)

#     print("Extracting params")
#     updated_params = None
#     if os.path.exists("latest_params.json"):
#         with open("latest_params.json", "r") as f:
#             updated_params = json.load(f)
#             print("$$$$ Updated Params on worker:", updated_params)
#     else:
#         print("No params found!")
#         updated_params = None

#     # Initialize the model
#     model = Sequential()
#     model.add(Dense(10, input_shape=(2,), activation='relu'))
#     model.add(Dense(1, activation='sigmoid'))

#     if updated_params is not None:
#         model.set_weights([np.array(p) for p in updated_params])

#     # Create loss function
#     loss_fn = tf.keras.losses.BinaryCrossentropy()

#     # Prepare data batches
#     if args.test_data == False:
#         batch_size = 32
#         train_dataset = tf.data.Dataset.from_tensor_slices((X_train_scaled, y))
#         train_dataset = train_dataset.shuffle(buffer_size=1024).batch(batch_size)


#     if args.test_data == True:
#         print("Evaluating model on test data inside container...")
#         # evaluate_model(model, X, y)
#         results = model.evaluate(X_test_scaled, y)
#         print(f"Test Loss: {results[0]}, Test Accuracy: {results[1]}")
#     else:        
#         print("Computing params")
#         # compute_gradients(model, X_tensor, y_tensor, output_path=args.output_path, worker_id = args.worker_id, result_filename = args.result_filename)

#         # Custom training loop
#         for x_batch, y_batch in train_dataset:
#             with tf.GradientTape() as tape:
#                 predictions = model(x_batch, training=True)
#                 loss = loss_fn(y_batch, predictions)
            
#             gradients = tape.gradient(loss, model.trainable_variables)

#             # Collect gradients into dict:
#             grad_dict = {}
#             for var, grad in zip(model.trainable_variables, gradients):
#                 grad_dict[var.name] = grad.numpy().tolist()

# Import necessary libraries
# import numpy as np
# import argparse
# import pandas as pd
# import uuid
# import os
# import json
# import tensorflow as tf
# from sklearn.preprocessing import StandardScaler
# from tensorflow.keras.models import Sequential
# from tensorflow.keras.layers import Dense

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()    
#     parser.add_argument("--output_path", type=str, default="/app/results/grads.json")
#     parser.add_argument("--worker_id", type=str, default=str(uuid.uuid4()))
#     parser.add_argument("--result_filename", type=str, default=f"res-random-{uuid.uuid4()}.json")
#     parser.add_argument("--test_data", action='store_true')    
#     args = parser.parse_args()

#     # Load CSV data
#     print("Loading data...")
#     local_filename = "test.csv" if args.test_data else "data.csv"
#     df = pd.read_csv(local_filename).dropna()

#     X = df.drop(columns=["Target"]).values
#     y = df["Target"].values.reshape(-1, 1)

#     # Scale the features (always fit_transform for simplicity)
#     scaler = StandardScaler()
#     X_scaled = scaler.fit_transform(X)

#     print("Extracting params...")
#     updated_params = None
#     if os.path.exists("latest_params.json"):
#         with open("latest_params.json", "r") as f:
#             updated_params = json.load(f)
#             print("$$$$ Updated Params on worker:", updated_params)
#     else:
#         print("No params found!")

#     # Initialize the model
#     model = Sequential([
#         Dense(10, input_shape=(X_scaled.shape[1],), activation='relu'),
#         Dense(1, activation='sigmoid')
#     ])

#     # Load weights if available
#     if updated_params is not None:
#         model.set_weights([np.array(p) for p in updated_params])

#     # Loss function
#     loss_fn = tf.keras.losses.BinaryCrossentropy()

#     if args.test_data:
#         print("Evaluating model on test data inside container...")
#         results = model.evaluate(X_scaled, y, verbose=1)
#         print(f"Test Loss: {results[0]}, Test Accuracy: {results[1]}")
#     else:
#         print("Computing gradients...")
#         # Prepare training batches
#         batch_size = 32
#         train_dataset = tf.data.Dataset.from_tensor_slices((X_scaled, y))
#         train_dataset = train_dataset.shuffle(buffer_size=1024).batch(batch_size)

#         # Custom training loop
#         grad_dict = {}
#         for x_batch, y_batch in train_dataset:
#             with tf.GradientTape() as tape:
#                 predictions = model(x_batch, training=True)
#                 loss = loss_fn(y_batch, predictions)
            
#             gradients = tape.gradient(loss, model.trainable_variables)

#             # Collect gradients into dictionary
#             for var, grad in zip(model.trainable_variables, gradients):
#                 grad_dict[var.name] = grad.numpy().tolist()

#         # Save gradients
#         os.makedirs(os.path.dirname(args.output_path), exist_ok=True)
#         with open(args.output_path, "w") as f:
#             json.dump({
#                 "worker_id": str(args.worker_id),
#                 "result_filename": args.result_filename,
#                 "gradients": grad_dict
#             }, f)
#         print(f"Gradients saved to {args.output_path}")


import torch
import torch.nn as nn
import os, uuid
import json
import argparse
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

class ShallowDeepNN(nn.Module):
    def __init__(self, input_dim):
        super(ShallowDeepNN, self).__init__()
        # First layer (shallow layer)
        self.layer1 = nn.Linear(input_dim, 64)
        self.relu = nn.ReLU()
        
        # Second layer (deep layer)
        self.layer2 = nn.Linear(64, 32)
        self.layer3 = nn.Linear(32, 1)  # Output layer

    def forward(self, x):
        x = self.relu(self.layer1(x))  # Shallow layer with ReLU activation
        x = self.relu(self.layer2(x))  # Deep layer
        x = torch.sigmoid(self.layer3(x))  # Sigmoid activation for binary classification
        return x

# Worker to compute gradients and update weights
def compute_gradients(model, data, target, output_path="/app/results/grads.json", worker_id=uuid.uuid4(), result_filename=f"res-random-{uuid.uuid4()}.json"):
    criterion = nn.BCELoss()
    output = model(data)
    loss = criterion(output, target)
    loss.backward()  # Backpropagate to compute gradients

    grads_list = []
    for name, param in model.named_parameters():
        if param.grad is not None:
            layer, param_type = name.split(".")  # e.g. 'layer1.weight' → 'layer1', 'weight'
            grads_list.append({
                "layer": layer,
                "type": param_type,
                "values": param.grad.detach().cpu().numpy().tolist()  # Convert to numpy before serialization
            })

    results_dir = output_path
    results_path = os.path.join(results_dir, result_filename)
    os.makedirs(results_dir, exist_ok=True)

    # Save gradients to file
    print("Param computation complete. Writing file to volume at:", results_path)
    with open(results_path, 'w') as f:
        json.dump(grads_list, f)

    return grads_list

def evaluate_model(model, X, y):
    model.eval()  # Set model to evaluation mode
    X_tensor = torch.tensor(X, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.float32)
    
    with torch.no_grad():
        outputs = model(X_tensor)
        preds = (outputs > 0.5).float()  # Binarize predictions

    y_true = y_tensor.numpy()
    y_pred = preds.numpy()

    # Compute evaluation metrics
    print("Accuracy:", accuracy_score(y_true, y_pred))
    print("Precision:", precision_score(y_true, y_pred))
    print("Recall:", recall_score(y_true, y_pred))
    print("F1 Score:", f1_score(y_true, y_pred))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()    
    parser.add_argument("--output_path", type=str, default="/app/results/grads.json")
    parser.add_argument("--worker_id", type=str, default=uuid.uuid4())
    parser.add_argument("--result_filename", type=str, default=f"res-random-{uuid.uuid4()}.json")
    parser.add_argument("--test_data", action='store_true')    
    args = parser.parse_args()

    # Load CSV data
    print("Loading data")
    local_filename = "test.csv" if args.test_data else "data.csv"
    df = pd.read_csv(local_filename) 
    df = df.dropna()
    
    # Separate features and target
    X = df[["Feature1", "Feature2"]].values  # Shape (num_samples, 2)
    y = df["Target"].values.reshape(-1, 1)   # Shape (num_samples, 1)

    # Normalize the data
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    # Normalize the data
    print("Normalizing data")
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    
    # Convert to PyTorch tensors
    print("Converting data to tensors")
    X_tensor = torch.tensor(X, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.float32)


    print("Extracting params")
    updated_params = None
    if os.path.exists("latest_params.json"):
        with open("latest_params.json", "r") as f:
            updated_params = json.load(f)
            print("$$$$ Updated Params on worker:", updated_params)
    else:
        print("No params found!")
        updated_params = None

    print("Creating Model")
    model = ShallowDeepNN(input_dim=X.shape[1])

    print("Loading params")
    print("Model weights:", model.layer1.weight)
    print("Model bias:", model.layer1.bias)
    if updated_params:
        with torch.no_grad():
            # Manually set the model parameters (if any)
            model.layer1.weight.copy_(torch.tensor(updated_params["layer1"]["weight"]))
            model.layer1.bias.copy_(torch.tensor(updated_params["layer1"]["bias"]))
            model.layer2.weight.copy_(torch.tensor(updated_params["layer2"]["weight"]))
            model.layer2.bias.copy_(torch.tensor(updated_params["layer2"]["bias"]))
            model.layer3.weight.copy_(torch.tensor(updated_params["layer3"]["weight"]))
            model.layer3.bias.copy_(torch.tensor(updated_params["layer3"]["bias"]))
            print("Adding params manually complete!")
    
    if args.test_data == True:
        print("Evaluating model on test data inside container...")
        evaluate_model(model, X, y)
    else:        
        print("Computing params")
        compute_gradients(model, X_tensor, y_tensor, output_path=args.output_path, worker_id=args.worker_id, result_filename=args.result_filename)
