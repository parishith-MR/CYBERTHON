import requests
import networkx as nx
from django.shortcuts import render
from django.http import JsonResponse
from pyvis.network import Network
from django.views.decorators.csrf import csrf_exempt

MORALIS_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6ImZmNmE5NmEzLWE5NjUtNDEwNy1iZGIyLTI5N2E2YTc4NzI2NSIsIm9yZ0lkIjoiNDI5NDYyIiwidXNlcklkIjoiNDQxNzQ5IiwidHlwZUlkIjoiY2E3YjA5N2YtYzE3Mi00MTIzLTg5MTQtMmI5MmUyNTM0MDFiIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3Mzg2ODczNzksImV4cCI6NDg5NDQ0NzM3OX0.8RLifPzimTbzeBqnY4Q9AiWb2GdyEIKExDv34m46If8"

def fetch_transactions(wallet_address, chain="eth"):
    """Fetch transactions using Moralis API with enhanced error handling and debugging."""
    url = f"https://deep-index.moralis.io/api/v2/{wallet_address}?chain={chain}"
    
    headers = {"X-API-Key": MORALIS_API_KEY}
    try:
        print(f"Fetching transactions for wallet: {wallet_address}")  # Debug print
        response = requests.get(url, headers=headers)
        print(f"API Response Status Code: {response.status_code}")  # Debug print
        
        # Print the first part of the response for debugging
        print(f"API Response: {response.text[:500]}")  # Show first 500 chars
        
        response.raise_for_status()
        data = response.json()
        
        # Additional validation
        if not isinstance(data, dict):
            print(f"Unexpected response format: {type(data)}")
            return []
            
        transactions = data.get("result", [])
        print(f"Found {len(transactions)} transactions")  # Debug print
        
        if not transactions:
            # Check if the wallet address is valid
            if not is_valid_ethereum_address(wallet_address):
                print(f"Invalid Ethereum address format: {wallet_address}")
                return []
                
            # Check if the wallet exists but has no transactions
            print("No transactions found for this wallet")
            return []
            
        return transactions
        
    except requests.RequestException as e:
        print(f"API Request Error: {str(e)}")
        return []
    except ValueError as e:
        print(f"JSON Parsing Error: {str(e)}")
        return []
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
        return []

def is_valid_ethereum_address(address):
    """Validate Ethereum address format."""
    import re
    # Check if address matches Ethereum address format (0x followed by 40 hex characters)
    pattern = re.compile(r'^0x[a-fA-F0-9]{40}$')
    return bool(pattern.match(address))

@csrf_exempt
def home(request):
    """Enhanced home view with better error handling."""
    if request.method == "POST":
        wallet_address = request.POST.get("wallet_address", "").strip()
        chain = request.POST.get("chain", "eth")
        
        if not wallet_address:
            return JsonResponse({
                "status": "error",
                "message": "Wallet address is required"
            })
            
        if not is_valid_ethereum_address(wallet_address):
            return JsonResponse({
                "status": "error",
                "message": "Invalid Ethereum address format"
            })
        
        # Fetch transactions
        transactions = fetch_transactions(wallet_address, chain)
        
        if not transactions:
            return JsonResponse({
                "status": "warning",
                "message": "No transactions found for this wallet",
                "data": {
                    "wallet_address": wallet_address,
                    "total_transactions": 0,
                    "transaction_volume": 0,
                    "fraud_score": 0,
                    "suspicious_activities": []
                }
            })
        
        # Generate new visualization only if we have transactions
        graph_success = generate_spider_graph(transactions)
        
        # Analyze transactions
        analysis_results = analyze_transactions(wallet_address, transactions)
        
        if not graph_success:
            analysis_results["graph_error"] = "Failed to generate transaction graph"
        
        return JsonResponse({
            "status": "success",
            "message": "Analysis complete!",
            "data": analysis_results
        })
    
    return render(request, "analysis/home.html")

def generate_spider_graph(transactions):
    """Generate a spider graph visualization."""
    if not transactions:
        return False
    
    G = nx.DiGraph()
    
    for tx in transactions:
        sender = tx.get("from_address")
        receiver = tx.get("to_address")
        value = float(tx.get("value", 0)) / 10**18  # Convert to ETH
        
        if sender and receiver:
            sender_node = sender.lower()
            receiver_node = receiver.lower()
            G.add_node(sender_node, color='blue', title=f"Wallet: {sender_node}")
            G.add_node(receiver_node, color='blue', title=f"Wallet: {receiver_node}")
            G.add_edge(sender_node, receiver_node, value=value, title=f"{value:.4f} ETH")

    net = Network(height="600px", width="100%", directed=True)
    net.from_nx(G)
    net.set_options("""
    {
        "physics": {
            "forceAtlas2Based": {
                "gravitationalConstant": -100,
                "springLength": 100
            },
            "minVelocity": 0.75,
            "solver": "forceAtlas2Based"
        }
    }
    """)
    
    try:
        net.save_graph("static/graph.html")
        return True
    except Exception as e:
        print(f"Error saving graph: {e}")
        return False

def analyze_transactions(wallet_address, transactions):
    """Analyze transactions for suspicious patterns."""
    if not transactions:
        return {
            "wallet_address": wallet_address,
            "total_transactions": 0,
            "transaction_volume": 0,
            "fraud_score": 0,
            "suspicious_activities": []
        }

    total_volume = sum(float(tx.get("value", 0)) / 10**18 for tx in transactions)
    
    # Calculate fraud score and detect patterns
    fraud_score = 0
    suspicious_patterns = []
    
    # Add your fraud detection logic here
    if len(transactions) > 50:
        fraud_score += 30
        suspicious_patterns.append("High transaction volume detected")
    
    # Cap the fraud score at 100
    fraud_score = min(fraud_score, 100)
    
    return {
        "wallet_address": wallet_address,
        "total_transactions": len(transactions),
        "transaction_volume": total_volume,
        "fraud_score": fraud_score,
        "suspicious_activities": suspicious_patterns
    }

