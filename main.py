from data.nhtsa_data import nhtsa_combine_makes_and_models
from database.db import init_db
from database.load_csv import load_csv
from data.noisy_data.load_noise import load_noise


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
    print("Generating noisy variants...")
    load_noise()

    print("Done! Noisy variants generated and loaded into DB.")

