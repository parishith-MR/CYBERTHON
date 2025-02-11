
from web3 import Web3
import os

# Load API key & private key securely
ALCHEMY_API_KEY = "tFLRKUwUC2HgVmitiLmPikLSS0leLtAZ"
PRIVATE_KEY = "47ec1a6221f1b8095c6cbe61b1e3b16cec01543f6ae540b9c58cfc4937ecb97a"


# Connect to Alchemy Sepolia
w3 = Web3(Web3.HTTPProvider(f"https://eth-sepolia.g.alchemy.com/v2/{ALCHEMY_API_KEY}"))

# Sender wallet details
SENDER_ADDRESS = w3.eth.account.from_key(PRIVATE_KEY).address

def send_dust_transaction(recipient_wallets):
    """Send dust transactions to a list of wallets."""
    dust_amount = w3.to_wei(0.00001, 'ether')  # Tiny ETH amount
    gas_price = w3.to_wei('5', 'gwei')  # Adjust based on Sepolia conditions

    results = []
    nonce = w3.eth.get_transaction_count(SENDER_ADDRESS)

    for recipient in recipient_wallets:
        try:
            txn = {
                'to': recipient,
                'value': dust_amount,
                'gas': 21000,
                'gasPrice': gas_price,
                'nonce': nonce,
                'chainId': 11155111  # Sepolia chain ID
            }
            signed_txn = w3.eth.account.sign_transaction(txn, PRIVATE_KEY)
            txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)  # Fixed

            results.append({"wallet": recipient, "tx_hash": txn_hash.hex()})
            nonce += 1  # Increment nonce for the next transaction

            print(f"✅ Sent dust to {recipient} - TX: {txn_hash.hex()}")

        except Exception as e:
            print(f"❌ Error sending dust to {recipient}: {str(e)}")
            results.append({"wallet": recipient, "error": str(e)})

    return results

