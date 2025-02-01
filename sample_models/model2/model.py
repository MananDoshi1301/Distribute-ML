import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam

# Generate sample data
def generate_sample_data():
    np.random.seed(42)
    X = np.random.randn(1000, 5)  # 1000 samples, 5 features
    y = (X[:, 0] + X[:, 1] > 0).astype(int)  # Binary classification
    
    # Create DataFrame
    columns = [f'feature_{i}' for i in range(5)] + ['target']
    data = np.column_stack([X, y])
    df = pd.DataFrame(data, columns=columns)
    
    # Save to CSV
    df.to_csv('data.csv', index=False)
    print("Sample data saved to data.csv")

# Build and train neural network
def train_neural_network():
    # Load data
    df = pd.read_csv('data.csv')
    X = df.drop('target', axis=1)
    y = df['target']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Build model
    model = Sequential([
        Dense(10, activation='relu', input_shape=(X_train.shape[1],)),
        Dense(5, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    
    # Compile model
    model.compile(optimizer=Adam(learning_rate=0.01), 
                  loss='binary_crossentropy', 
                  metrics=['accuracy'])
    
    # Train model
    history = model.fit(
        X_train_scaled, y_train, 
        validation_split=0.2, 
        epochs=50, 
        batch_size=32, 
        verbose=1
    )
    
    # Evaluate model
    test_loss, test_accuracy = model.evaluate(X_test_scaled, y_test)
    print(f"\nTest Accuracy: {test_accuracy:.4f}")
    
    return model

# Main execution
if __name__ == '__main__':
    generate_sample_data()
    # model = train_neural_network()