"""
The StorePDBComponent stores the PDB file given a method.
This method consists of two options 'local' and 'remote'.
The 'local' method is used to store the PDB file locally in the provided folder.
The 'remote' method will use the GCP storage bucket to store the PDB file.
"""
import logging
import os
import pandas as pd
from fondant.component import PandasTransformComponent
from google.cloud import storage # pylint: disable=import-error


logger = logging.getLogger(__name__)


class StorePDBComponent(PandasTransformComponent):
	"""
	The StorePDBComponent stores the PDB file given a method.
	This method consists of two options 'local' and 'remote'.
	The 'local' method is used to store the PDB file locally in the provided folder.
	The 'remote' method will use the GCP storage bucket to store the PDB file.
	"""

	def __init__(self, method: str, local_pdb_path: str, bucket_name: str,
			  project_id: str, google_cloud_credentials_path: str):
		# pylint: disable=super-init-not-called
		# pylint: disable=too-many-arguments

		if method not in ["local", "remote"]:
			raise ValueError("method must be either 'local' or 'remote'")
		self.method = method

		if method == "local":
			self.local_pdb_files_path = local_pdb_path

		else:
			os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_cloud_credentials_path
			os.environ["GOOGLE_CLOUD_PROJECT"] = project_id

			self.bucket_name = bucket_name
			self.project_id = project_id

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""Perform the transformation on the dataframe."""

		if self.method == "local":
			dataframe = self.store_local_pdb_files(dataframe)

		else:
			storage_client = storage.Client(self.project_id)
			bucket = storage_client.get_bucket(self.bucket_name)
			dataframe = self.store_remote_pdb_files(dataframe, bucket)

		return dataframe

	def store_remote_pdb_files(self, dataframe: pd.DataFrame, bucket: storage.Bucket) -> pd.DataFrame:
		"""Save the remote PDB files and filter out the ones that already exist."""
		# pylint: disable=no-self-use

		dataframe.apply(lambda row: bucket.blob(
			row.sequence_checksum).upload_from_string(row.pdb_string), axis=1)

		return dataframe

	def store_local_pdb_files(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""Store the local PDB files and filter out the ones that already exist."""

		for row in dataframe.itertuples():
			with open(self.local_pdb_files_path + row.sequence_checksum + ".pdb", "w+") as f:
				f.write(row.pdb_string)

		return dataframe
