<!-- * Disribute ML

1. To run this project, install and start redis, mysql and docker which can be downloaded using brew (brew install redis) (brew services start redis)
2. Install python and project_requirements.txt file to have all libraries required to run the project (pip install project_requirements.txt) preferably inside a virtual environment
3. Login mysql cmd line, and run `source ./master_server/main.sql` to create tables
4. Change config key for mysql inside config_server/conf/base.py
5. Run the following servers:
    1. ./config_server/server.py (python3 server.py)
    2. ./file_transfer_app/server.py (fastapi dev server.py)
    3. ./master_server/server.py (python3 server.py)
    4. ./master_server (rq worker high) (Spawn any number of workers)

5. To run training, set the conf file, make sure, model.py, requirements.txt, data.csv are present in the root of the directory.
6. Run python3 train.py -->


<!-- # Distribute ML

## Overview
Distribute ML is a distributed machine learning project designed to facilitate efficient training and management of machine learning models. This guide provides instructions on how to set up and run the project.

---

## Prerequisites
Before running this project, ensure the following dependencies are installed:
- **Redis**: Install and start using Homebrew.
  ```bash
  brew install redis
  brew services start redis
  ```
- **MySQL**: Install and start using Homebrew.
- **Docker**: Install Docker for containerization.
- **Python**: Ensure Python is installed on your system.

---

## Setup

### 1. Install Project Dependencies
- Use a virtual environment to isolate the project dependencies:
  ```bash
  python3 -m venv env
  source env/bin/activate
  ```
- Install the required libraries from the `project_requirements.txt` file:
  ```bash
  pip install -r project_requirements.txt
  ```

### 2. Configure MySQL
- Login to MySQL command line:
  ```bash
  mysql -u <username> -p
  ```
- Run the following command to create the necessary tables:
  ```sql
  source ./master_server/main.sql;
  ```

### 3. Update MySQL Configuration
- Update the MySQL configuration key in the file `config_server/conf/base.py` to match your MySQL setup.

---

## Running the Project

### 1. Start the Servers
Run the following servers in separate terminal windows:
1. **Config Server**:
   ```bash
   cd ./config_server
   python3 server.py
   ```
2. **File Transfer App**:
   ```bash
   cd ./file_transfer_app
   fastapi dev server.py
   ```
3. **Master Server**:
   ```bash
   cd ./master_server
   python3 server.py
   ```
4. **Worker Process**:
   ```bash
   cd ./master_server
   rq worker high
   ```
   > Spawn any number of workers as required.

---

### 2. Running Training
To run the training process:
1. Ensure the following files are present in the root directory:
   - `model.py`
   - `requirements.txt`
   - `data.csv`
2. Set the configuration in the `conf` file.
3. Execute the training script:
   ```bash
   python3 train.py
   ```

---

## Notes
- It is recommended to use a virtual environment for managing dependencies.
- Ensure all servers and database services are running prior to executing the training script.
- For additional customization, refer to the configuration files specific to each server.

---

Happy Coding! -->


<div align="center">

# DistributeML

<!-- ![DistributeML Logo](https://via.placeholder.com/150) -->

**A robust platform for distributed machine learning training and model management**

[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-supported-brightgreen.svg)](https://www.docker.com/)

</div>

## ✨ Overview

**DistributeML** empowers data scientists to train and manage machine learning models across distributed environments with minimal configuration. Scale your training processes efficiently while focusing on what matters most: your models, not infrastructure.

## 🔍 Features

- 🚀 **Distributed Training** - Train models across multiple nodes seamlessly
- 📊 **Model Management** - Version control and track all your ML experiments
- 🛠️ **Easy Deployment** - Deploy models with simple commands
- ⚙️ **Resource Optimization** - Intelligent allocation of computing resources
- 🔄 **Horizontal Scaling** - Add workers dynamically as needed

## 📋 Prerequisites

Before running this project, ensure you have:

| Dependency | Installation Command | Purpose |
|------------|----------------------|---------|
| **Redis**  | `brew install redis && brew services start redis` | Job queue and caching |
| **MySQL**  | `brew install mysql && brew services start mysql` | Metadata storage |
| **Docker** | [Install Docker](https://www.docker.com/) | Containerization |
| **Python** | Version 3.7+ recommended | Runtime environment |

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/distributeml.git
cd distributeml
```

### 2. Install Project Dependencies

```bash
# Create and activate virtual environment
python3 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
pip install -r project_requirements.txt
```

### 3. Configure MySQL

```bash
# Login to MySQL
mysql -u <username> -p

# Set up database tables
mysql> source ./master_server/main.sql;
```

### 4. Update Configuration

Edit the MySQL configuration in `config_server/conf/base.py` to match your setup:

```python
# Example configuration
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'distributeml'
}
```

## ⚙️ Configuration

Create a `conf.py` file in your project root to define your model training parameters:

```python
from distribute_ml.master import Master
from torch import optim
import random

class DistributionConfig:
    # Path to your model definition file
    MODEL_ENTRYPOINT = "./model.py" 
    
    # Path to your training data
    MODEL_DATA = "./data.csv"
    
    # Path to requirements file for your model
    MODEL_REQUIREMENTS = "./requirements.txt"  # (default=requirements.txt)
    
    # Type of output from the task
    TASK_OUTPUT = "weight"    
    
    # Optimizer parameters
    OPTIMIZER_PARAMS = {
        "lr": 0.01,
        "momentum": 0.9
    }
    
    # Initial model parameters
    INITIAL_PARAMS = {
        "linear": {
            "weight": [[0.0 for _ in range(30)]],  
            "bias": [0.0]
        }
    }

    # Number of partitions for data distribution
    TASK_PARTITION = 2  # (default=10)

    # Training parameters
    TOTAL_ITERATIONS = 4
    
    # Data splitting ratios
    TRAIN_SPLIT = 0.7
    TEST_SPLIT = 0.15
    VALIDATION_SPLIT = 0.15
```

## 🔌 Running the System

### 1. Start Services

Launch each service in a separate terminal window:

<details>
<summary>Config Server</summary>

```bash
cd ./config_server
python3 server.py
```
</details>

<details>
<summary>File Transfer Service</summary>

```bash
cd ./file_transfer_app
fastapi dev server.py
```
</details>

<details>
<summary>Master Server</summary>

```bash
cd ./master_server
python3 server.py
```
</details>

<details>
<summary>Worker Processes</summary>

```bash
cd ./master_server
rq worker high  # Spawn multiple workers as needed
```
</details>

### 2. Running Training Jobs

Prepare your training by ensuring these files are in the root directory:
- `model.py` - Your model definition
- `requirements.txt` - Dependencies for your model
- `data.csv` - Training dataset
- `conf.py` - Configuration parameters

Then execute:

```bash
python3 train.py
```

## 📊 Architecture

```
distributeml/
├── config_server/    # Configuration management
├── file_transfer_app/# File transfer services
├── master_server/    # Job scheduling and orchestration
├── workers/          # Distributed worker processes
└── client/           # Client interface
```

## 📝 Example Model File

Below is a simple example of what your `model.py` file might look like:

```python
import torch
import torch.nn as nn
import torch.optim as optim
import os, uuid
import json
import argparse
import pandas as pd
import numpy as np
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
```

## 🔧 Advanced Configuration

Customize your deployment by modifying configuration files:

```yaml
# Example of worker configuration
workers:
  min_count: 2
  max_count: 10
  auto_scale: true
  resource_limits:
    cpu: 4
    memory: "8G"
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a pull request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <b>Built with ❤️ for the ML community</b>
</div>