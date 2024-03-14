"""
The LocalPDBComponent class is a component that takes in a dataframe, sends each sequence to the Hugging Face API and returns the tertiary structure of the protein sequence using a local parquet file as the cache.
"""
import logging
import os
from typing import Dict, List
import requests
import pandas as pd
from dotenv import load_dotenv
from fondant.component import PandasTransformComponent

# Load the environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)


class LocalPDBComponent(PandasTransformComponent):
	"""The LocalPDBComponent class is a component that takes in a dataframe, sends each sequence to the Hugging Face API and returns the tertiary structure of the protein sequence."""

	def __init__(self, pdb_file_path: str):
		self.HF_API_KEY = os.getenv("HF_API_KEY")
		self.HF_ENDPOINT_URL = os.getenv("HF_ENDPOINT_URL")
		self.pdb_file_path = pdb_file_path

		self.df_pdb_local = pd.read_parquet(self.pdb_file_path)

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""The transform method takes in a dataframe, sends each sequence to the Hugging Face API and returns the tertiary structure of the protein sequence."""

		if (self.HF_API_KEY is None) or (self.HF_ENDPOINT_URL is None):
			logger.error(
				"The Hugging Face API key or endpoint URL is not set.")
			return dataframe

		dataframe = self.apply_local_transform(dataframe)

		return dataframe

	def apply_local_transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""The apply_local_transform method takes in a dataframe, sends each sequence to the Hugging Face API and returns the tertiary structure of the protein sequence."""

		dataframe = self.merge_local_pdb_strings(dataframe)
		payload = self.prepare_payload_local(dataframe)
		response = self.send_query(payload)

		dataframe = self.merge_response_to_dataframe(dataframe, response)

		self.df_pdb_local = self.merge_new_pdbs_to_local(
			self.df_pdb_local, response)
		self.df_pdb_local.to_parquet(self.pdb_file_path, index=False)

		return dataframe

	def merge_new_pdbs_to_local(self, df_pdb_local: pd.DataFrame, response: List[Dict[str, str]]) -> pd.DataFrame:
		"""
		Merge the response from the Hugging Face API with the local dataframe.
		"""
		if response is None or len(response) == 0:
			return df_pdb_local

		response_df = pd.DataFrame(response)
		response_df = response_df.rename(
			columns={"id": "sequence_id", "pdb": "pdb_string"})

		# Concatenate response_df with df_pdb_local
		df_pdb_local = pd.concat(
			[df_pdb_local, response_df], ignore_index=True)

		return df_pdb_local

	def merge_local_pdb_strings(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""
		Merge the local parquet file with the input dataframe.
		This method adds the pdb_string column to the dataframe, but not all the sequences will have a pdb_string. This is because the local parquet file only contains the generated ones. The ones that are not in the local parquet file will be sent to the Hugging Face API.
		"""

		local_pdb_sequence_ids = self.df_pdb_local["sequence_id"].tolist()

		dataframe["pdb_string"] = ""

		for row in dataframe.itertuples():
			if row.sequence_id in local_pdb_sequence_ids:
				dataframe.at[row.Index, "pdb_string"] = self.df_pdb_local[self.df_pdb_local["sequence_id"]
																		== row.sequence_id]["pdb_string"].values[0]
			else:
				dataframe.at[row.Index, "pdb_string"] = ""

		return dataframe

	def prepare_payload_local(self, dataframe: pd.DataFrame) -> Dict[str, List[Dict[str, str]]]:
		"""
		Prepare the payload by combining the existing pdb strings with the dataframe. Keep track of the sequences that don't have the pdb string in the local parquet file and send them to the Hugging Face API.
		Returns the payload and the dataframe.
		"""

		ids_and_sequences = []

		for row in dataframe.itertuples():
			if row.pdb_string == "":
				ids_and_sequences.append(
					{"id": row.sequence_id, "sequence": row.sequence})

		return {"inputs": ids_and_sequences}

	def merge_response_to_dataframe(self, dataframe: pd.DataFrame, response: List[Dict[str, str]]) -> pd.DataFrame:
		"""Merge the response from the Hugging Face API with the original dataframe."""

		# Check if response is empty
		if response is None or len(response) == 0:
			return dataframe

		for row in dataframe.itertuples():
			for item in response:
				if item["id"] == row.sequence_id:
					dataframe.at[row.Index, "pdb_string"] = item["pdb"]

		return dataframe

	def send_query(self, payload: list) -> list:
		"""
		Send the payload to the Hugging Face API and return the response.
		"""
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
