"""
The StorePDBComponent stores the PDB file given a method. This method consists of two options 'local' and 'remote'. The 'local' method is used to store the PDB file locally in the '/data/pdb_files' folder. The 'remote' method will use the GCP storage bucket to store the PDB file.
"""
import logging
import os
import pandas as pd
from fondant.component import PandasTransformComponent
from dotenv import load_dotenv
from google.cloud import storage

# Set up logging
logger = logging.getLogger(__name__)

# Load the environment variables
load_dotenv()

# Get the path to the service account JSON key file from the environment variables
service_account_key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Set GOOGLE_APPLICATION_CREDENTIALS environment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_key_path

# Set GOOGLE_CLOUD_PROJECT environment variable
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("PROJECT_ID")


class StorePDBComponent(PandasTransformComponent):
	"""
	The StorePDBComponent stores the PDB file given a method. This method consists of two options 'local' and 'remote'. The 'local' method is used to store the PDB file locally in the '/data/pdb_files' folder. The 'remote' method will use the GCP storage bucket to store the PDB file. 
	"""

	def __init__(self, method: str):
		if method not in ["local", "remote"]:
			raise ValueError("method must be either 'local' or 'remote'")

		self.method = method
		self.local_pdb_files_path = "/data/pdb_files/"

		if method == "remote":
			self.bucket_name = os.getenv("BUCKET_NAME")
			self.project_id = os.getenv("PROJECT_ID")

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""Perform the transformation on the dataframe."""

		if self.method == "local":
			dataframe = self.store_local_pdb_files(dataframe)
		if self.method == "remote":
			self.storage_client = storage.Client(self.project_id)
			self.bucket = self.storage_client.get_bucket(self.bucket_name)
			dataframe = self.store_remote_pdb_files(dataframe)

		return dataframe

	def store_remote_pdb_files(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""Save the remote PDB files and filter out the ones that already exist."""

		# Collect all blob names first
		blob_names = [blob.name for blob in self.bucket.list_blobs()]

		existing_blobs = [
			blob for blob in blob_names if blob in dataframe['sequence_id'].values]

		for row in dataframe.itertuples():
			if row.sequence_id not in existing_blobs:
				blob = self.bucket.blob(row.sequence_id)
				blob.upload_from_string(row.pdb_string)

				# remove the blob from the list of existing blobs
				existing_blobs.remove(row.sequence_id)

		return dataframe

	def store_local_pdb_files(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""Store the local PDB files and filter out the ones that already exist."""

		# create list of existing filenames of PDB files
		existing_pdb_files = []
		for filename in os.listdir(self.local_pdb_files_path):
			if filename.endswith(".pdb"):
				existing_pdb_files.append(filename.split(".")[0])

		# save the PDB files that don't exist yet
		for row in dataframe.itertuples():
			if row.sequence_id not in existing_pdb_files:
				with open(self.local_pdb_files_path + row.sequence_id + ".pdb", "w") as f:
					f.write(row.pdb_string)

		return dataframe
