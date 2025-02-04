import requests
import networkx as nx
from django.shortcuts import render
from django.http import JsonResponse
from pyvis.network import Network

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
    """Generate a graph visualization using PyVis."""
    G = nx.DiGraph()

    for tx in transactions:
        sender = tx["from_address"]
        receiver = tx["to_address"]
        value = int(tx["value"]) / 10**18  # Convert to ETH

        G.add_edge(sender, receiver, weight=value)

    net = Network(height="600px", width="100%", directed=True)
    net.from_nx(G)
    
    # Save to the static directory instead
    net.save_graph("static/graph.html")  # Changed from analysis/static/graph.html

def home(request):
    if request.method == "POST":
        wallet_address = request.POST.get("wallet_address")
        chain = request.POST.get("chain", "eth")

        transactions = fetch_transactions(wallet_address, chain)
        if transactions:
            generate_spider_graph(transactions)

        return JsonResponse({"status": "success", "message": "Graph generated!"})

    return render(request, "analysis/home.html")
