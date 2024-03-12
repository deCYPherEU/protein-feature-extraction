"""
The CloudPDBComponent class is a component that takes in a dataframe, sends each sequence to the Hugging Face API and returns the tertiary structure of the protein sequence using the cloud (GCP).
"""
import logging
import pandas as pd
from fondant.component import PandasTransformComponent
import os
from Bio.SeqUtils.CheckSum import crc64
import requests
from dotenv import load_dotenv
from typing import Dict, List, Tuple
from google.cloud import storage
import os

# Load the environment variables
load_dotenv()

# Get the path to the service account JSON key file from the environment variables
service_account_key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Set GOOGLE_APPLICATION_CREDENTIALS environment variable
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_key_path

# Set GOOGLE_CLOUD_PROJECT environment variable
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("PROJECT_ID")

# Set up logging
logger = logging.getLogger(__name__)

class CloudPDBComponent(PandasTransformComponent):
	"""The CloudPDBComponent class is a component that takes in a dataframe, sends each sequence to the Hugging Face API and returns the tertiary structure of the protein sequence."""

	def __init__(self):
		self.bucket_name = os.getenv("BUCKET_NAME")
		self.HF_API_KEY = os.getenv("HF_API_KEY")
		self.HF_ENDPOINT_URL = os.getenv("HF_ENDPOINT_URL")
		self.project_id = os.getenv("PROJECT_ID")

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""The transform method takes in a dataframe, sends each sequence to the Hugging Face API and returns the tertiary structure of the protein sequence."""

		storage_client = storage.Client(self.project_id)
		bucket = storage_client.get_bucket(self.bucket_name)

		if (self.HF_API_KEY is None) or (self.HF_ENDPOINT_URL is None):
			logger.error("The Hugging Face API key or endpoint URL is not set.")
			return dataframe
		
		if (self.bucket_name is None) or (self.project_id is None):
			logger.error("The bucket name or project id is not set.")
			return dataframe

		dataframe = self.apply_cloud_transform(dataframe, bucket)
		
		return dataframe
		
	
	def apply_cloud_transform(self, dataframe: pd.DataFrame, bucket) -> pd.DataFrame:
		"""The cloud_transform method takes in a dataframe, sends each sequence to the Hugging Face API and returns the tertiary structure of the protein sequence."""

		dataframe = self.apply_checksum(dataframe)

		payload, dataframe = self.prepare_payload_cloud(dataframe, bucket)
		response = self.send_query(payload)
		
		dataframe = self.merge_response_to_dataframe(dataframe, response)

		self.upload_to_cloud_storage(dataframe, bucket)
		
		return dataframe

	def apply_checksum(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""Apply a CRC64 checksum to each sequence and store the result in a new column."""

		dataframe["sequence_id"] = ""
		# Create a new column to store the pdb_string
		dataframe["pdb_string"] = ""
		
		for index, row in dataframe.iterrows():
			dataframe.at[index, "sequence_id"] = crc64(row["sequence"])
		
		return dataframe

	
	def prepare_payload_cloud(self, dataframe: pd.DataFrame, bucket) -> Tuple[Dict[str, List[Dict[str, str]]], pd.DataFrame]:
		"""
		Prepare the payload by performing a CRC64 checksum on each sequence and adding it to the inputs list.
		Returns the payload and the dataframe.
		"""

		ids_and_sequences = []

		# Collect all blob names first
		blob_names = [blob.name for blob in bucket.list_blobs()]

		# Check if the sequence is in the cloud storage
		for index, row in dataframe.iterrows():
			found = False
			for blob_name in blob_names:
				if row["sequence_id"] in blob_name:
					found = True
					# If the sequence is found in the cloud storage, update the dataframe
					row["pdb_string"] = self.get_blob_content(blob_name, bucket)
					row["sequence_id"] = blob_name
					dataframe.at[index, "pdb_string"] = row["pdb_string"]
					dataframe.at[index, "sequence_id"] = row["sequence_id"]

			if not found:
				# If the sequence is not in the cloud storage, add it to the payload
				ids_and_sequences.append({"id": crc64(row["sequence"]), "sequence": row["sequence"]})

		return {"inputs": ids_and_sequences}, dataframe
	
	def get_blob_content(self, blob_name: str, bucket) -> str:
		"""
		Get the content of a blob from the cloud storage.
		"""

		blob = bucket.blob(blob_name)
		return blob.download_as_string()


	def merge_response_to_dataframe(self, dataframe: pd.DataFrame, response: List[Dict[str, str]]) -> pd.DataFrame:
		"""Merge the response from the Hugging Face API with the original dataframe."""

		# Check if response is empty
		if response is None or len(response) == 0:
			return dataframe

		# Place merged data into the dataframe
		for index, row in dataframe.iterrows():
			for item in response:
				if item["id"] == row["sequence_id"]:
					dataframe.at[index, "pdb_string"] = item["pdb"]

		return dataframe


	def send_query(self, payload: list) -> list:
		# check if the payload contains any values for the "inputs" key
		if len(payload["inputs"]) == 0:
			return []

		try:
			response = requests.post(self.HF_ENDPOINT_URL,
									headers={
										"Accept": "application/json",
										"Authorization": f"Bearer {self.HF_API_KEY}",
										"Content-Type": "application/json",
									},
									json=payload)
			response.raise_for_status()
			return response.json()
		
		except requests.exceptions.RequestException as e:
			print("ERROR API request: ", e)
			return []


	def upload_to_cloud_storage(self, dataframe: pd.DataFrame, bucket) -> None:
		"""
		Upload the pdb files to the cloud storage if they are not already in the cloud storage.
		"""

		# check if the checksum is already in the cloud storage
		ids_in_cloud = [blob.name for blob in bucket.list_blobs()]

		for index, row in dataframe.iterrows():
			if row["sequence_id"] not in ids_in_cloud:
				blob = bucket.blob(row["sequence_id"])
				blob.upload_from_string(row["pdb_string"])
