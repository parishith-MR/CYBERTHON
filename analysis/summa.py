import requests
import networkx as nx
from django.shortcuts import render
from django.http import JsonResponse
from pyvis.network import Network
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
import matplotlib.pyplot as plt
from datetime import datetime

MORALIS_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6ImZmNmE5NmEzLWE5NjUtNDEwNy1iZGIyLTI5N2E2YTc4NzI2NSIsIm9yZ0lkIjoiNDI5NDYyIiwidXNlcklkIjoiNDQxNzQ5IiwidHlwZUlkIjoiY2E3YjA5N2YtYzE3Mi00MTIzLTg5MTQtMmI5MmUyNTM0MDFiIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3Mzg2ODczNzksImV4cCI6NDg5NDQ0NzM3OX0.8RLifPzimTbzeBqnY4Q9AiWb2GdyEIKExDv34m46If8"


def fetch_transactions(wallet_address, chain="eth"):
    """Fetch transactions using Moralis API."""
    url = f"https://deep-index.moralis.io/api/v2/{wallet_address}?chain={chain}"
    
    headers = {"X-API-Key": MORALIS_API_KEY}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json().get("result", [])
    return []

def generate_spider_graph(transactions):
    """Generate an enhanced graph visualization using PyVis."""
    if not transactions:
        print("No transactions to visualize.")
        return
    
    G = nx.DiGraph()
    
    for tx in transactions:
        sender = tx.get("from_address")
        receiver = tx.get("to_address")
        value = int(tx.get("value", 0)) / 10**18  
        
        if sender and receiver:
            sender_node = sender.lower()
            receiver_node = receiver.lower()
            G.add_node(sender_node, color='blue', title=f"Wallet: {sender_node}")
            G.add_node(receiver_node, color='blue', title=f"Wallet: {receiver_node}")
            
            G.add_edge(sender_node, receiver_node, value=value, title=f"{value:.4f} ETH")

    if len(G.nodes) == 0:
        print("No valid wallet nodes found in graph.")

    net = Network(height="600px", width="100%", directed=True)
    net.from_nx(G)
    net.set_options("""{ "physics": { "forceAtlas2Based": { "gravitationalConstant": -100, "springLength": 100 }, "minVelocity": 0.75, "solver": "forceAtlas2Based" }}""")
    net.save_graph("static/graph.html")

def analyze_wallet(wallet_address, chain="eth"):
    """Analyze wallet transactions and detect fraudulent patterns."""
    transactions = fetch_transactions(wallet_address, chain)

    # Example logic for computing fraud score
    fraud_score = 0  
    if len(transactions) > 50:
        fraud_score += 30  # More transactions = higher risk
    if detect_suspicious_activity(wallet_address):
        fraud_score += 20  # Suspicious activity detected
    if detect_blacklisted_interactions(wallet_address):
        fraud_score += 50  # Blacklisted address interaction = high risk
    if detect_rapid_high_value(wallet_address):
        fraud_score += 15  # Structuring detected
    if detect_circular_transactions(wallet_address):
        fraud_score += 20  # Mixing detected
    if detect_tumbling_activity(wallet_address):
        fraud_score += 25  # Tumbling detected
    if detect_chain_hopping(wallet_address):
        fraud_score += 30  # Cross-chain laundering
    if detect_sudden_large_inflows(wallet_address):
        fraud_score += 40  # Money mule behavior
    
    if fraud_score > 100:
        fraud_score = 100  # Max score cap

    return {
        "wallet_address": wallet_address,
        "total_transactions": len(transactions),
        "transaction_volume": sum(int(tx["value"]) / 10**18 for tx in transactions),
        "fraud_score": fraud_score,  # Send fraud score to frontend
    }

def detect_suspicious_activity(wallet_address):
    """Detects unusual transaction patterns such as rapid high-value transfers or circular transactions."""
    suspicious_patterns = []
    if detect_rapid_high_value(wallet_address):
        suspicious_patterns.append("Rapid high-value transactions detected.")
    if detect_circular_transactions(wallet_address):
        suspicious_patterns.append("Circular transactions detected.")
    if detect_blacklisted_interactions(wallet_address):
        suspicious_patterns.append("Interaction with blacklisted wallets detected.")
    if detect_tumbling_activity(wallet_address):
        suspicious_patterns.append("Tumbling/mixing activity detected.")
    if detect_chain_hopping(wallet_address):
        suspicious_patterns.append("Cross-chain laundering detected.")
    if detect_sudden_large_inflows(wallet_address):
        suspicious_patterns.append("Sudden large incoming transactions detected.")
    
    return suspicious_patterns

# ✅ Fixed: Rapid High-Value Transactions (Structuring)
def detect_rapid_high_value(wallet_address, threshold=5, time_window=10, min_value=1):
    transactions = fetch_transactions(wallet_address)
    if not transactions:
        return []
    now = timezone.now().timestamp()
    high_value_txs = [
        tx for tx in transactions if tx.get("value") and int(tx["value"]) / 10**18 >= min_value
        and (now - int(tx.get("timestamp", now))) <= time_window * 60
    ]
    return high_value_txs if len(high_value_txs) >= threshold else []

# ✅ Fixed: Circular Transactions (Self-Funding or Mixing)
def detect_circular_transactions(wallet_address):
    transactions = fetch_transactions(wallet_address)
    return [tx for tx in transactions if tx.get("from_address") == tx.get("to_address")]

# ✅ Fixed: Transactions with Known Illicit Addresses (Blacklisted Wallets)
BLACKLISTED_ADDRESSES = {"0x1234...abcd", "0xabcd...5678"}

def detect_blacklisted_interactions(wallet_address):
    transactions = fetch_transactions(wallet_address)
    return [tx for tx in transactions if tx.get("from_address") in BLACKLISTED_ADDRESSES or tx.get("to_address") in BLACKLISTED_ADDRESSES]

# ✅ Fixed: Tumbling / Mixing Services (Obfuscation)
def detect_tumbling_activity(wallet_address, max_time=10):
    transactions = fetch_transactions(wallet_address)
    suspicious_txs = []
    for tx in transactions:
        sender = tx.get("from_address")
        receiver = tx.get("to_address")
        timestamp = tx.get("timestamp")

        if timestamp is None:
            continue  

        related_txs = [
            t for t in transactions if t.get("from_address") == receiver and t.get("timestamp")
            and abs(int(t["timestamp"]) - int(timestamp)) < max_time * 60
        ]

        if related_txs:
            suspicious_txs.append({"tx_hash": tx["hash"], "forwarded_to": [t["to_address"] for t in related_txs]})

    return suspicious_txs

# ✅ Fixed: Chain Hopping (Cross-Chain Laundering)
def detect_chain_hopping(wallet_address):
    transactions = fetch_transactions(wallet_address)
    chains = set(tx.get("chain") for tx in transactions)
    return list(chains) if len(chains) > 1 else []

# ✅ Fixed: Sudden Large Incoming Transactions (Money Mule)
def detect_sudden_large_inflows(wallet_address, min_value=10):
    transactions = fetch_transactions(wallet_address)
    first_tx = next((tx for tx in transactions if tx.get("to_address") == wallet_address), None)
    return {"tx_hash": first_tx["hash"], "value": int(first_tx["value"]) / 10**18} if first_tx and int(first_tx["value"]) / 10**18 >= min_value else None

@csrf_exempt
def home(request):
    if request.method == "POST":
        wallet_address = request.POST.get("wallet_address")
        chain = request.POST.get("chain", "eth")

        # Perform analysis
        analysis_results = analyze_wallet(wallet_address, chain)

        return JsonResponse({
            "status": "success",
            "message": "Analysis complete!",
            "data": analysis_results
        })

    return render(request, "analysis/home.html")
