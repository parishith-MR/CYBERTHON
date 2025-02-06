# views.py
import requests
import networkx as nx
from django.shortcuts import render
from django.http import JsonResponse
from pyvis.network import Network
from .models import WalletConnection
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

MORALIS_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6ImZmNmE5NmEzLWE5NjUtNDEwNy1iZGIyLTI5N2E2YTc4NzI2NSIsIm9yZ0lkIjoiNDI5NDYyIiwidXNlcklkIjoiNDQxNzQ5IiwidHlwZUlkIjoiY2E3YjA5N2YtYzE3Mi00MTIzLTg5MTQtMmI5MmUyNTM0MDFiIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3Mzg2ODczNzksImV4cCI6NDg5NDQ0NzM3OX0.8RLifPzimTbzeBqnY4Q9AiWb2GdyEIKExDv34m46If8"

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def fetch_transactions(wallet_address, chain="eth"):
    """Fetch transactions using Moralis API."""
    url = f"https://deep-index.moralis.io/api/v2/{wallet_address}?chain={chain}"
    
    headers = {"X-API-Key": MORALIS_API_KEY}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json().get("result", [])
    return []

def generate_spider_graph(transactions, wallet_connections):
    """Generate an enhanced graph visualization using PyVis."""
    if not transactions:
        print("No transactions to visualize.")
        return
    
    G = nx.DiGraph()
    
    # Add transaction edges
    for tx in transactions:
        sender = tx.get("from_address")
        receiver = tx.get("to_address")
        value = int(tx.get("value", 0)) / 10**18  # Convert to ETH, avoid issues with missing 'value'
        
        if sender and receiver:
            # Add nodes with different colors based on IP tracking
            sender_node = sender.lower()
            receiver_node = receiver.lower()
            G.add_node(sender_node, color='red' if any(conn.wallet_address.lower() == sender_node for conn in wallet_connections) else 'blue', title=f"Wallet: {sender_node}")
            G.add_node(receiver_node, color='red' if any(conn.wallet_address.lower() == receiver_node for conn in wallet_connections) else 'blue', title=f"Wallet: {receiver_node}")
            
            G.add_edge(sender_node, receiver_node, value=value, title=f"{value:.4f} ETH")

    if len(G.nodes) == 0:
        print("No valid wallet nodes found in graph.")

    # Create and configure network
    net = Network(height="600px", width="100%", directed=True)
    net.from_nx(G)
    
    # Add physics options for better visualization
    net.set_options("""{ "physics": { "forceAtlas2Based": { "gravitationalConstant": -100, "springLength": 100 }, "minVelocity": 0.75, "solver": "forceAtlas2Based" }}""")
    
    # Save graph
    net.save_graph("static/graph.html")


def analyze_wallet(request, wallet_address, chain="eth"):
    """Analyze wallet transactions and IP connections."""
    # Get recent connections for this wallet
    recent_connections = WalletConnection.objects.filter(
        wallet_address=wallet_address,
        connection_time__gte=timezone.now() - timedelta(days=30)
    ).order_by('-connection_time')
    
    # Fetch transactions
    transactions = fetch_transactions(wallet_address, chain)
    
    # Generate visualization
    generate_spider_graph(transactions, recent_connections)
    
    # Prepare analysis results
    analysis = {
        'wallet_address': wallet_address,
        'total_transactions': len(transactions),
        'unique_ips': recent_connections.values('ip_address').distinct().count(),
        'recent_connections': list(recent_connections.values(
            'ip_address', 'connection_time', 'user_agent'
        ))[:10],
        'transaction_volume': sum(
            int(tx['value']) / 10**18 for tx in transactions
        )
    }
    
    return analysis
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def home(request):
    if request.method == "POST":
        wallet_address = request.POST.get("wallet_address")
        chain = request.POST.get("chain", "eth")
        
        # Track the current connection
        WalletConnection.objects.create(
            wallet_address=wallet_address,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            connection_type='web3'
        )
        
        # Perform analysis
        analysis_results = analyze_wallet(request, wallet_address, chain)
        
        return JsonResponse({
            "status": "success",
            "message": "Analysis complete!",
            "data": analysis_results
        })

    return render(request, "analysis/home.html")
