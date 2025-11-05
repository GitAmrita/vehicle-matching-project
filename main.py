from data.nhtsa_data import nhtsa_combine_makes_and_models
from database.db import init_db
from database.load_csv import load_csv
from data.noisy_data.load_noise import load_noise
from data.embeddings.quadrant import build_embeddings
from data.embeddings.test_quadrant import *
from database.elasticsearch_client import *


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
    test_connection()


