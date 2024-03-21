"""
The FilterPDBComponent is a component that takes in a dataframe and, based on the method given, it loads up the PDB files and keep the ones that don't exist yet. This component compares the existing PDB files with the ones in the dataframe using the checksum and filters out the ones that already exist. 
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


class FilterPDBComponent(PandasTransformComponent):
	"""
	The FilterPDBComponent is a component that takes in a dataframe and, based on the method given, it loads up the PDB files and keep the ones that don't exist yet. This component compares the existing PDB files with the ones in the dataframe using the checksum and filters out the ones that already exist. 
	"""

	def __init__(self, method: str, pdb_path: str):
		if method not in ["local", "remote"]:
			raise ValueError("method must be either 'local' or 'remote'")
		self.method = method
		self.local_pdb_files_path = pdb_path

		if method == "remote":
			self.bucket_name = os.getenv("BUCKET_NAME")
			self.project_id = os.getenv("PROJECT_ID")

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""Perform the transformation on the dataframe."""

		if self.method == "local":
			dataframe = self.load_local_pdb_files(dataframe)
		if self.method == "remote":
			self.storage_client = storage.Client(self.project_id)
			self.bucket = self.storage_client.get_bucket(self.bucket_name)
			dataframe = self.load_remote_pdb_files(dataframe)

		return dataframe

	def load_remote_pdb_files(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""Load the remote PDB files and filter out the ones that already exist."""

		# Collect all blob names first
		blob_names = [blob.name for blob in self.bucket.list_blobs()]

		existing_blobs = [
			blob for blob in blob_names if blob in dataframe['sequence_id'].values]

		dataframe['pdb_string'] = ""

		for row in dataframe.itertuples():
			if row.sequence_id in existing_blobs:
				blob = self.bucket.blob(row.sequence_id)
				logger.info(f"Downloading {row.sequence_id} from the bucket")
				dataframe.at[row.Index,
							'pdb_string'] = blob.download_as_string()

				# remove the blob from the list of existing blobs
				existing_blobs.remove(row.sequence_id)

		return dataframe

	def load_local_pdb_files(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""Load the local PDB files and filter out the ones that already exist."""

		# create dict of existing PDB files
		existing_pdb_files = {}
		for filename in os.listdir(self.local_pdb_files_path):
			with open(os.path.join(self.local_pdb_files_path, filename), "r") as file:
				existing_pdb_files[filename] = file.read()

		# place the content of the PDB files in the dataframe of the existing PDB files
		dataframe['pdb_string'] = dataframe['sequence_id'].apply(
			lambda x: existing_pdb_files.get(x, ""))

		return dataframe
