import pandas as pd
from crypto_analyzer import CryptoAnalyzer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import pickle
import os

def train_model(transactions_path, labels_path):
    """Train the fraud detection model"""
    # Load data
    transactions = pd.read_json(transactions_path)
    labels = pd.read_csv(labels_path)
    
    # Prepare features and labels
    X, y = prepare_training_data(transactions.to_dict('records'), 
                               dict(zip(labels['tx_hash'], labels['is_illegal'])))
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Initialize and train model
    model = RandomForestClassifier(n_estimators=200, max_depth=20, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test)
    print("\nModel Performance:")
    print(classification_report(y_test, y_pred))
    
    # Save model
    os.makedirs('analysis/ml/models', exist_ok=True)
    with open('analysis/ml/models/fraud_detection_model.pkl', 'wb') as f:
        pickle.dump(model, f)

if __name__ == "__main__":
    train_model('data/transactions.json', 'data/labels.csv')