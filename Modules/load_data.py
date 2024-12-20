# Please ensure your kaggle.json file (with kaggle API key) is in the correct folder
# ~/.kaggle/kaggle.json for LINUX

# Importing libraries
import kaggle
from pathlib import Path
import json
import pandas as pd


def load_data(dataset, data_folder):
    """load_data

    Downloads dataset through kaggle API

    Args:
        dataset (str): link to dataset given by <kaggle username>/<dataset>
        data_folder (str): Path to data folder
    """

    # Automatically looks for the kaggle.json file and authenticates user
    kaggle.api.authenticate()

    # Downloading dataset ...
    kaggle.api.dataset_download_files(dataset, path=data_folder, unzip=True)


def merge_dfs(transaction_data_csv, cards_data_csv, data_folder):
    """merge_dfs

    Merges card data with transaction data and export to pickle in the data folder

    Args:
        transaction_data_csv (str): path to transaction_data.csv
        cards_data_csv (str): path to cards_data.csv
        data_folder (str): Absolute path to data folder
    """
    # Turning CSV into pandas df

    transaction_data_df = pd.read_csv(transaction_data_csv)
    cards_data_df = pd.read_csv(cards_data_csv)

    # Load in the fraud jsons
    with open(data_folder + "/train_fraud_labels.json", "r") as file:
        fraud_data = json.load(file)

    # Load in mcc codes
    # with open(data_folder + "/mcc_codes.json", "r") as file:
    #    mcc_data = json.load(file)

    # Function to add a new column to the data set using the JSON

    # Making into a pandas series
    fraud_data = pd.DataFrame(fraud_data)

    # resetting index
    fraud_data.reset_index(inplace=True)

    # Renaming index to id for later merge
    fraud_data.rename(columns={"index": "id"}, inplace=True)

    # Changing id column to int type
    fraud_data["id"] = fraud_data["id"].astype(int)

    # Dropping client column in cards df as it is redunadant
    cards_data_df = cards_data_df.drop(columns=["client_id"])

    # Users data has no identifier to match with the transaction data
    # Merging card data with transaction data
    merged_df = transaction_data_df.merge(
        cards_data_df,
        how="inner",
        left_on="card_id",
        right_on="id",
        suffixes=("_T", "_C"),
    )

    # Adding target column to merged df by merging on id_T and id
    merged_df = merged_df.merge(
        fraud_data, how="inner", left_on="id_T", right_on="id", suffixes=("_T", "_C")
    )

    # Dropping id_C and id_T created from merge and equivalent to id (id of transaction)
    merged_df = merged_df.drop(columns=["id_C", "id_T"])

    # Mapping mcc codes
    # merged_df["mcc"] = merged_df["mcc"].map(mcc_data)

    # Saving merged_df to pickle
    merged_df.to_pickle(data_folder + "/merged_data.pkl")
