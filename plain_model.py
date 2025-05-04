# from sklearn.datasets import load_breast_cancer
# from sklearn.linear_model import LogisticRegression
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import accuracy_score

# #load the following dataset 
# X, y = load_breast_cancer(return_X_y=True)

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=23)

# clf = LogisticRegression(max_iter=10000, random_state=0)
# clf.fit(X_train, y_train)

# acc = accuracy_score(y_test, clf.predict(X_test)) * 100
# print(f"Logistic Regression model accuracy: {acc:.2f}%")

import time
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Start timer
start_time = time.time()

# Load the dataset
X, y = load_breast_cancer(return_X_y=True)

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=23)

# Train the model
clf = LogisticRegression(max_iter=10000, random_state=0)
clf.fit(X_train, y_train)

# Evaluate the model
acc = accuracy_score(y_test, clf.predict(X_test)) * 100
print(f"Logistic Regression model accuracy: {acc:.2f}%")

# Calculate execution time
end_time = time.time()
execution_time = end_time - start_time
print(f"Total runtime: {execution_time:.4f} seconds")