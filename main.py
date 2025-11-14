from data.nhtsa_data import nhtsa_combine_makes_and_models
from database.db import init_db
from database.load_csv import load_csv
from data.noisy_data.load_noise import load_noise
from data.embeddings.quadrant import build_embeddings
from data.embeddings.test_quadrant import *
from es_module.elasticsearch_client import *
from es_module.indexing import create_index, build_index, get_index_stats
from es_module.test_elasticsearch import *


if __name__ == "__main__":
    # "Get dataset from NHTSA"
    # nhtsa_combine_makes_and_models()

    # "Insert dataset into db"
    # print("Initializing database...")
    # init_db(reset=True)

    # print("Loading CSV data...")
    # load_csv("make_model_year.csv")

    # print("Done! Data inserted into vehicle.db")

    # "Generate noisy variants"
    # print("Generating noisy variants...")
    # load_noise()

    # Build embeddings
    # uploaded = build_embeddings(limit=1000, offset=0)
    # print(f"Uploaded {uploaded} points to Qdrant")
    
    # Run test file
    # view_collection(limit=5)
    # demo_search()

    # evaluate()
    
    # You can also call individual functions:
    # search("toyota camry")  # Search for specific vehicle

    # Test connection to Elasticsearch
    # test_connection()
    
    # Index data into Elasticsearch
    # print("Creating Elasticsearch index...")
    # create_index(recreate=True)  # Set recreate=True to delete and recreate
    
    # print("Indexing vehicle data...")
    # indexed = build_index(limit=1000, offset=0)
    # print(f"Indexed {indexed} documents")
    
    # Index statistics:
    # stats = get_index_stats()
    # if stats:
    #     print(f"  Documents: {stats['document_count']}")
    #     print(f"  Size: {stats['size_mb']} MB")
    
    # Test Elasticsearch search
    print("\n=== Testing Elasticsearch Search ===")
    # view_index(limit=50)  # View sample documents
    es_demo_search(use_fuzzy=True)  # Demo search with fuzzy matching
    # test_fuzzy_matching()  # Test fuzzy matching capabilities
    
    # Evaluate search quality
    # metrics = evaluate(limit=30, k=10, use_fuzzy=True)
    # print(f"\n📊 Evaluation Results:")
    # print(f"   Precision: {metrics['Precision']:.4f}")
    # print(f"   Recall: {metrics['Recall']:.4f}")
    
    # Compare fuzzy vs exact matching
    # compare_fuzzy_vs_exact(limit=30, k=10)
    
    pass  # Placeholder - uncomment tests above to run
