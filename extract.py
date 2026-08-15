import pandas as pd
import os
import requests


def get_data():
    source = os.getenv('SOURCE')

    if source == 'csv':
        return _get_data_csv()

    if source == 'api':
        return _get_data_api()

    raise ValueError(f"Invalid source")


def _get_data_api():
    eddress = str(os.getenv("API_PATH"))
    r = requests.get(eddress)
    r.raise_for_status()
    return pd.DataFrame(r.json())

def _get_data_csv():
    path = str(os.getenv("FOLDER_PATH"))
    df = pd.read_csv(path)
    return df

def _get_sql():
    pass