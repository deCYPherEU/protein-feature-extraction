"""
The HuggingFaceEndpointComponent class is a component that takes in a dataframe, sends each sequence to the Hugging Face API and returns the tertiary structure of the protein sequence.
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

# Set up logging
logger = logging.getLogger(__name__)

class HuggingFaceEndpointComponent(PandasTransformComponent):
	"""The HuggingFaceEndpointComponent class is a component that takes in a dataframe, sends each sequence to the Hugging Face API and returns the tertiary structure of the protein sequence."""

	def __init__(self, method: str):
		self.method = method

		# Load the environment variables
		self.bucket_name = os.getenv("BUCKET_NAME")
		self.project_id = os.getenv("PROJECT_ID")
		self.HF_API_KEY = os.getenv("HF_API_KEY")
		self.HF_ENDPOINT_URL = os.getenv("HF_ENDPOINT_URL")

		self.storage_client = storage.Client(project=self.project_id)
		self.bucket = self.storage_client.get_bucket(self.bucket_name)


	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""The transform method takes in a dataframe, sends each sequence to the Hugging Face API and returns the tertiary structure of the protein sequence."""

		if (self.HF_API_KEY is None) or (self.HF_ENDPOINT_URL is None):
			logger.error("The Hugging Face API key or endpoint URL is not set.")
			return dataframe
		
		if (self.bucket_name is None) or (self.project_id is None):
			logger.error("The bucket name or project id is not set.")
			return dataframe
		
		if self.method not in ["local", "cloud"]:
			logger.error("The method must be either 'local' or 'cloud'.")
			return dataframe

		if self.method == "local":
			return self.apply_local_transform(dataframe)
		
		if self.method == "cloud":
			return self.apply_cloud_transform(dataframe)
		
		return dataframe

	
	def apply_cloud_transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""The cloud_transform method takes in a dataframe, sends each sequence to the Hugging Face API and returns the tertiary structure of the protein sequence."""

		dataframe = self.apply_checksum(dataframe)

		payload, dataframe = self.prepare_payload_cloud(dataframe)
		# response = self.send_query(payload)
		
		# Mock response
		response = [
			{
				"id": "CRC-94CF2EE011C80480",
				"pdb": "pdb_file"
			},
			{
				"id": "CRC-68D748EC385E9BEC",
				"pdb": "pdb_file_2"
			},
			{
				"id": "CRC-3B9E0764E7D3C737",
				"pdb": "pdb_file_3"
			},
			{
				"id": "CRC-B08C4E4E86E87F17",
				"pdb": "pdb_file_4"
			},
			{
				"id": "CRC-747F108552578E1D",
				"pdb": "pdb_file_5"
			}
		]

		dataframe = self.merge_response_to_dataframe(dataframe, response)

		self.upload_to_cloud_storage(dataframe)
		
		return dataframe

	def upload_to_cloud_storage(self, dataframe: pd.DataFrame) -> None:
		"""
		Upload the pdb files to the cloud storage if they are not already in the cloud storage.
		"""

		# check if the checksum is already in the cloud storage
		ids_in_cloud = [blob.name for blob in self.bucket.list_blobs()]

		for index, row in dataframe.iterrows():
			if row["sequence_id"] not in ids_in_cloud:
				blob = self.bucket.blob(row["sequence_id"])
				blob.upload_from_string(row["pdb_string"])


	def apply_checksum(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""Apply a CRC64 checksum to each sequence and store the result in a new column."""

		dataframe["sequence_id"] = ""
		# Create a new column to store the pdb_string
		dataframe["pdb_string"] = ""
		
		for index, row in dataframe.iterrows():
			dataframe.at[index, "sequence_id"] = crc64(row["sequence"])
		
		return dataframe
	
	def prepare_payload_cloud(self, dataframe: pd.DataFrame) -> Tuple[Dict[str, List[Dict[str, str]]], pd.DataFrame]:
		"""
		Prepare the payload by performing a CRC64 checksum on each sequence and adding it to the inputs list.
		Returns the payload and the dataframe.
		"""

		ids_and_sequences = []

		# Collect all blob names first
		blob_names = [blob.name for blob in self.bucket.list_blobs()]

		# Check if the sequence is in the cloud storage
		for index, row in dataframe.iterrows():
			found = False
			for blob_name in blob_names:
				if row["sequence_id"] in blob_name:
					found = True
					# If the sequence is found in the cloud storage, update the dataframe
					row["pdb_string"] = self.get_blob_content(blob_name)  # Assuming you have a method to get blob content
					row["sequence_id"] = blob_name
					break

			if not found:
				# If the sequence is not in the cloud storage, add it to the payload
				ids_and_sequences.append({"id": crc64(row["sequence"]), "sequence": row["sequence"]})

		return {"inputs": ids_and_sequences}, dataframe
	
	def get_blob_content(self, blob_name: str) -> str:
		"""
		Get the content of a blob from the cloud storage.
		"""

		blob = self.bucket.blob(blob_name)
		return blob.download_as_string()


	def apply_local_transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""The local_transform method takes in a dataframe, sends each sequence to the Hugging Face API and returns the tertiary structure of the protein sequence."""

		dataframe = self.apply_checksum(dataframe)
		payload = self.prepare_payload_local(dataframe)
		# response = self.send_query(payload)

		# Mock response
		response = [
			{
				"id": "CRC-94CF2EE011C80480",
				"pdb": "pdb_file"
			},
			{
				"id": "CRC-68D748EC385E9BEC",
				"pdb": "pdb_file_2"
			},
			{
				"id": "CRC-3B9E0764E7D3C737",
				"pdb": "pdb_file_3"
			},
			{
				"id": "CRC-B08C4E4E86E87F17",
				"pdb": "pdb_file_4"
			},
			{
				"id": "CRC-747F108552578E1D",
				"pdb": "pdb_file_5"
			}
		]

		dataframe = self.merge_response_to_dataframe(dataframe, response)

		return dataframe

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


	def prepare_payload_local(self, dataframe: pd.DataFrame) -> Dict[str, List[Dict[str, str]]]:
		"""Prepare the payload by performing a CRC64 checksum on each sequence and adding it to the inputs list."""

		ids_and_sequences = []

		for index, row in dataframe.iterrows():
			sequence = row["sequence"]
			checksum = crc64(sequence)
			ids_and_sequences.append({"id": checksum, "sequence": sequence})
		

		return {"inputs": ids_and_sequences}


	def send_query(self, payload: list) -> list:
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
