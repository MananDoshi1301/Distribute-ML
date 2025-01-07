import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
# import joblib


class PhishingURLModel:
    def __init__(self, data_path="data.csv", model_path="phishing_model.pkl"):
        self.data_path = data_path
        self.model_path = model_path
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
    
    def load_data(self):
        """Load and preprocess the data."""
        print("Loading data...")
        df = pd.read_csv(self.data_path)
        if "label_encoded" not in df.columns:
            raise ValueError("Dataset must have a 'label_encoded' column.")
        
        X = df.drop(columns=["label_encoded"])
        y = df["label_encoded"]
        return train_test_split(X, y, test_size=0.2, random_state=42)
    
    def train(self):
        """Train the model on the dataset."""
        print("Training model...")
        X_train, X_test, y_train, y_test = self.load_data()
        self.model.fit(X_train, y_train)
        
        # Evaluate the model
        predictions = self.model.predict(X_test)
        print(f"Accuracy: {accuracy_score(y_test, predictions):.2f}")
        print("Classification Report:")
        print(classification_report(y_test, predictions))
        
        # Save the model
        # self.save_model()
    
    # def save_model(self):
    #     """Save the trained model to disk."""
    #     print(f"Saving model to {self.model_path}...")
    #     joblib.dump(self.model, self.model_path)
    
    # def load_model(self):
    #     """Load the saved model."""
    #     print(f"Loading model from {self.model_path}...")
    #     self.model = joblib.load(self.model_path)
    
    # def predict(self, features):
    #     """Predict using the trained model."""
    #     if not self.model:
    #         raise ValueError("Model not loaded. Call `load_model` first.")
    #     return self.model.predict(features)


if __name__ == "__main__":
    # Replace 'data.csv' with the actual dataset path
    model = PhishingURLModel(data_path="data.csv")
    model.train()
