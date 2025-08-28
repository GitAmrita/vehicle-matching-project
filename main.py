from data.nhtsa_data import nhtsa_combine_makes_and_models
from database.db import init_db
from database.load_csv import load_csv


if __name__ == "__main__":
    # "Get dataset from NHTSA"
    # nhtsa_combine_makes_and_models()

    # "Insert dataset into db"
    print("Initializing database...")
    init_db()

    print("Loading CSV data...")
    load_csv("make_model_year.csv")  # replace with your CSV file path

    print("Done! Data inserted into vehicle.db")
