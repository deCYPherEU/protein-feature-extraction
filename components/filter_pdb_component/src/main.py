"""
The FilterPDBComponent is a component that takes in a dataframe and, based on the method given, it loads up the PDB files and keep the ones that don't exist yet. This component compares the existing PDB files with the ones in the dataframe using the checksum and filters out the ones that already exist. 
"""

import logging
import os
import pandas as pd
from fondant.component import PandasTransformComponent
from google.cloud import storage

# Set up logging
logger = logging.getLogger(__name__)


class FilterPDBComponent(PandasTransformComponent):
	"""
	The FilterPDBComponent is a component that takes in a dataframe and, based on the method given, it loads up the PDB files and keep the ones that don't exist yet. This component compares the existing PDB files with the ones in the dataframe using the checksum and filters out the ones that already exist. 
	"""

	def __init__(self, method: str, pdb_path: str, bucket_name: str, project_id: str, google_cloud_credentials_path: str):

		if method not in ["local", "remote"]:
			raise ValueError("method must be either 'local' or 'remote'")
		self.method = method

		if method == "local":
			self.local_pdb_files_path = pdb_path

		else:
			os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_cloud_credentials_path
			os.environ["GOOGLE_CLOUD_PROJECT"] = project_id

			self.bucket_name = bucket_name
			self.project_id = project_id

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""Perform the transformation on the dataframe."""

		if self.method == "local":
			dataframe = self.load_local_pdb_files(dataframe)

		else:
			storage_client = storage.Client(self.project_id)
			bucket = storage_client.get_bucket(self.bucket_name)
			dataframe = self.load_remote_pdb_files(dataframe, bucket)

		return dataframe

	def load_remote_pdb_files(self, dataframe: pd.DataFrame, bucket: storage.Bucket) -> pd.DataFrame:
		"""Load the remote PDB files and filter out the ones that already exist."""

		# Collect all blob names first
		blob_names = [blob.name for blob in bucket.list_blobs()]

		existing_blobs = [
			blob for blob in blob_names if blob in dataframe['sequence_checksum'].values]

		dataframe['pdb_string'] = ""

		for row in dataframe.itertuples():
			if row.sequence_checksum in existing_blobs:
				blob = bucket.blob(row.sequence_checksum)
				logger.info(
					f"Downloading {row.sequence_checksum} from the bucket")
				dataframe.at[row.Index,
							'pdb_string'] = blob.download_as_string()

				# remove the blob from the list of existing blobs
				existing_blobs.remove(row.sequence_checksum)

		return dataframe

	def load_local_pdb_files(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""Load the local PDB files and filter out the ones that already exist."""

		# create dict of existing PDB files
		existing_pdb_files = {}
		for filename in os.listdir(self.local_pdb_files_path):
			with open(os.path.join(self.local_pdb_files_path, filename), "r") as file:
				existing_pdb_files[filename.split(".")[0]] = file.read()

		dataframe['pdb_string'] = dataframe['sequence_checksum'].apply(
			lambda x: existing_pdb_files.get(x, ""))

		return dataframe
