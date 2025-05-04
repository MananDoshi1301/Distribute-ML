import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score

import time

start_time = time.time()
# Load data from CSV
data = pd.read_csv('data.csv')
print(data.columns)

# Features and label
X = data.drop('label_encoded', axis=1)
y = data['label_encoded']

# Feature scaling
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train logistic regression model
model = LogisticRegression()
model.fit(X_scaled, y)

# Predict on training set
y_pred = model.predict(X_scaled)

# Evaluate the model
print("Accuracy:", accuracy_score(y, y_pred))
print("Classification Report:\n", classification_report(y, y_pred))


end_time = time.time()
execution_time = end_time - start_time
print(f"Total runtime: {execution_time:.4f} seconds")