import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pickle
import os
from datetime import datetime
import networkx as nx

class CryptoAnalyzer:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = 'analysis/ml/models/fraud_detection_model.pkl'
        self.load_model()
        
    def load_model(self):
        """Load trained model if exists"""
        if os.path.exists(self.model_path):
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
    
    def extract_features(self, transaction):
        """Extract features from a single transaction"""
        return {
            'value': float(transaction.get('value', 0)) / 10**18,
            'gas_price': float(transaction.get('gas_price', 0)),
            'gas_used': float(transaction.get('gas_used', 0)),
            'hour_of_day': datetime.fromtimestamp(int(transaction.get('block_timestamp', 0))).hour,
            'day_of_week': datetime.fromtimestamp(int(transaction.get('block_timestamp', 0))).weekday(),
            'input_data_length': len(transaction.get('input', '')),
            'is_token_transfer': 1 if transaction.get('input', '').startswith('0xa9059cbb') else 0
        }
    
    def extract_advanced_features(self, transactions):
        """Extract features from transactions safely"""
        try:
            # Default features if no transactions
            if not transactions:
                return {
                    'tx_per_hour': 0,
                    'avg_value': 0,
                    'unique_addresses': 0,
                    'total_volume': 0,
                    'tx_count': 0
                }
            
            # Process transactions
            values = []
            addresses = set()
            timestamps = []
            
            for tx in transactions:
                try:
                    value = float(tx.get('value', '0')) / 10**18
                    values.append(value)
                    addresses.add(tx.get('from_address', '').lower())
                    addresses.add(tx.get('to_address', '').lower())
                    if tx.get('block_timestamp'):
                        timestamps.append(pd.to_datetime(tx.get('block_timestamp')))
                except (ValueError, TypeError) as e:
                    print(f"Error processing transaction: {e}")
                    continue
            
            # Calculate features
            features = {
                'tx_count': len(transactions),
                'total_volume': sum(values),
                'avg_value': sum(values) / len(values) if values else 0,
                'unique_addresses': len(addresses)
            }
            
            # Calculate transactions per hour
            if len(timestamps) >= 2:
                time_diff = max(timestamps) - min(timestamps)
                hours_diff = time_diff.total_seconds() / 3600
                features['tx_per_hour'] = len(transactions) / max(hours_diff, 1)
            else:
                features['tx_per_hour'] = 0
                
            return features
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            return {
                'tx_per_hour': 0,
                'avg_value': 0,
                'unique_addresses': 0,
                'total_volume': 0,
                'tx_count': 0
            }
    
    def predict_risk_score(self, transactions):
        """Predict risk score using ML model"""
        if not self.model:
            return self._rule_based_score(transactions)
            
        try:
            # Extract features from all transactions
            features = []
            for tx in transactions:
                features.append(self.extract_features(tx))
            
            # Convert to DataFrame and scale features
            X = pd.DataFrame(features)
            X_scaled = self.scaler.transform(X)
            
            # Get probability of illegal class
            probabilities = self.model.predict_proba(X_scaled)
            
            # Return average probability of illegal class
            return float(np.mean(probabilities[:, 1]) * 100)
            
        except Exception as e:
            print(f"Error in ML prediction: {e}")
            return self._rule_based_score(transactions)
    
    def _rule_based_score(self, transactions):
        """Fallback rule-based scoring"""
        features = self.extract_advanced_features(transactions)
        
        risk_score = 0
        if features['tx_per_hour'] > 10:
            risk_score += 20
        if features['avg_value'] > 100:
            risk_score += 15
        if features['unique_addresses'] > 50:
            risk_score += 25
            
        return min(risk_score, 100)