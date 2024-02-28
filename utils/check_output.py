import pandas as pd

# load parquet data from a folder and return a pandas dataframe
def load_from_parquet(dataset_uri: str) -> pd.DataFrame:
	return pd.read_parquet(dataset_uri)


df = load_from_parquet('./data/export/')
print(df.head())