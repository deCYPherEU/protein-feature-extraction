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

# Load the environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

# Access the environment variables
HF_API_KEY = os.getenv("HF_API_KEY")
HF_ENDPOINT_URL = os.getenv("HF_API_KEY")


class HuggingFaceEndpointComponent(PandasTransformComponent):
	"""The HuggingFaceEndpointComponent class is a component that takes in a dataframe, sends each sequence to the Hugging Face API and returns the tertiary structure of the protein sequence."""

	def __init__(self, method: str):
		self.method = method

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""The transform method takes in a dataframe, sends each sequence to the Hugging Face API and returns the tertiary structure of the protein sequence."""

		if (HF_API_KEY is None) or (HF_ENDPOINT_URL is None):
			logger.error("The Hugging Face API key or endpoint URL is not set.")
			return dataframe

		if self.method == "local":
			return self.apply_local_transform(dataframe)

		return dataframe


	def apply_local_transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""The local_transform method takes in a dataframe, sends each sequence to the Hugging Face API and returns the tertiary structure of the protein sequence."""

		payload = self.prepare_payload(dataframe)
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
		
		# Merge payload and response based on id
		merged_data = []
		for item in payload['inputs']:
			for resp in response:
				if item['id'] == resp['id']:
					merged_data.append({**item, **resp})
					break

		# Create columns
		dataframe["pdb_string"] = ""
		dataframe["sequence_id"] = ""

		# Place merged data into the dataframe
		for index, row in dataframe.iterrows():
			for merged_item in merged_data:
				if row["sequence"] == merged_item["sequence"]:
					dataframe.at[index, "pdb_string"] = merged_item["pdb"]
					dataframe.at[index, "sequence_id"] = merged_item["id"]
		

		return dataframe


	def prepare_payload(self, dataframe: pd.DataFrame) -> None:
		"""Prepare the payload by performing a CRC64 checksum on each sequence and adding it to the inputs list."""

		ids_and_sequences = []

		for index, row in dataframe.iterrows():
			sequence = row["sequence"]
			checksum = crc64(sequence)
			ids_and_sequences.append({"id": checksum, "sequence": sequence})
		

		return {"inputs": ids_and_sequences}


	def send_query(self, payload: list) -> list:
		try:
			response = requests.post(HF_ENDPOINT_URL,
									headers={
										"Accept": "application/json",
										"Authorization": f"Bearer {HF_API_KEY}",
										"Content-Type": "application/json",
									},
									json=payload)
			response.raise_for_status()
			return response.json()
		
		except requests.exceptions.RequestException as e:
			print("ERROR API request: ", e)
			return []
