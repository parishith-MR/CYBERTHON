import pandas as pd
import numpy as np
from datetime import datetime

def prepare_training_data(transactions, labels):
    """
    Prepare training data from transaction history
    
    Args:
        transactions: List of transaction dictionaries
        labels: Dictionary mapping transaction hashes to labels (0=legal, 1=illegal)
    """
    features = []
    target = []
    
    for tx in transactions:
        tx_hash = tx.get('hash')
        
        # Extract features
        feature_dict = {
            'value': float(tx.get('value', 0)) / 10**18,  # Convert to ETH
            'gas_price': float(tx.get('gas_price', 0)),
            'gas_used': float(tx.get('gas_used', 0)),
            'hour_of_day': datetime.fromtimestamp(int(tx.get('block_timestamp', 0))).hour,
            'day_of_week': datetime.fromtimestamp(int(tx.get('block_timestamp', 0))).weekday(),
            'input_data_length': len(tx.get('input', '')),
            'has_contract_interaction': 1 if tx.get('to_address') in known_contract_addresses else 0,
            'is_token_transfer': 1 if tx.get('input', '').startswith('0xa9059cbb') else 0
        }
        
        features.append(feature_dict)
        target.append(labels.get(tx_hash, 0))  # Default to legal if not labeled
        
    return pd.DataFrame(features), np.array(target)