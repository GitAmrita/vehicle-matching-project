#!/usr/bin/env python3
"""
Test file for Qdrant collection functionality
"""

from data.embeddings.quadrant import client, embedding_model, COLLECTION
from database.db import get_noisy_variants
from qdrant_client import models
from data.embeddings.evaluation_metrics import precision_recall
import re


def view_collection(collection_name: str = COLLECTION, limit: int = 10):
    """
    View collection information and sample points.
    """
    try:
        # Get collection info
        collection_info = client.get_collection(collection_name)
        print(f"📊 Collection: {collection_name}")
        print(f"   Points count: {collection_info.points_count}")
        print(f"   Vector size: {collection_info.config.params.vectors.size}")
        print(f"   Distance: {collection_info.config.params.vectors.distance}")
        
        # Get sample points
        print(f"\n🔍 Sample points (first {limit}):")
        points = client.scroll(
            collection_name=collection_name,
            limit=limit,
            with_payload=True,
            with_vectors=False  # Don't show vectors (too long)
        )[0]
        
        for i, point in enumerate(points, 1):
            print(f"   {i}. ID: {point.id}")
            print(f"      Make: {point.payload.get('make')}")
            print(f"      Model: {point.payload.get('model')}")
            print(f"      Year: {point.payload.get('year')}")
            print(f"      Text: {point.payload.get('normalized_text')}")
            print()
            
    except Exception as e:
        print(f"❌ Error viewing collection: {e}")


def search(query: str, top_k: int = 10):
    """
    Search for similar vehicles using local embeddings.
    """
    # Try to capture a year to filter (optional)
    year_match = re.search(r"\b(19\d{2}|20\d{2})\b", query)
    q_filter = None
    if year_match:
        year = int(year_match.group(0))
        q_filter = models.Filter(
            must=[models.FieldCondition(key="year", match=models.MatchValue(value=year))]
        )

    # Generate embedding for the query using FastEmbed
    query_embedding = list(embedding_model.embed([query.lower()]))[0]
    
    # Search in Qdrant
    res = client.query_points(
        collection_name=COLLECTION,
        query=query_embedding.tolist(),
        query_filter=q_filter,
        limit=top_k,
        with_payload=True,
    )
    
    return [
        {
            "score": round(p.score, 4),
            "id": p.id,
            "make": p.payload.get("make"),
            "model": p.payload.get("model"),
            "year": p.payload.get("year"),
        }
        for p in res.points
    ]


def demo_search(queries: list = None):

    """
    Demo search functionality with sample queries.
    """
    if queries is None:
        queries = ["2015 fabrication llc"]
    
    print("🔍 Testing search functionality")
    print("=" * 50)
    
    for query in queries:
        print(f"\n🔍 Searching for: '{query}'")
        results = search(query, top_k=3)
        for i, result in enumerate(results, 1):
            print(f"   {i}. {result['year']} {result['make']} {result['model']} (score: {result['score']})")

def evaluate(limit=5, k=3):
    """
    search_fn: function that takes noisy_string -> returns ranked list of dicts
    noisy_variants: iterable of dicts {noisy_string, make_id, model_id, year}
    """
    total_precision = 0
    total_recall = 0
    total_queries = 0


    noisy_variants = get_noisy_variants(limit=limit)

    for row in noisy_variants:
        noisy_string, model_id, make_id, year = row
        truth = (make_id, model_id, year)
        results = search(noisy_string, k)

        # --- Precision/Recall ---
        correct, retrieved = precision_recall(results, truth)
        total_precision += correct
        total_recall += correct  # since each query has 1 relevant item
        total_queries += 1


    metrics = {
        "Precision": total_precision / total_queries,
        "Recall": total_recall / total_queries,
    }
    return metrics
