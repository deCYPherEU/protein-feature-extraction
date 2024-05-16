"""
The PredictProtein3DStructureComponent is a component that takes
in a dataframe and sends the sequences to the HuggingFace ESMFold Endpoint
to predict the tertiary structures of the proteins.
The component returns the dataframe with the predicted tertiary structures.
"""
import logging
import os
from fondant.component import PandasTransformComponent
import pandas as pd
from dotenv import load_dotenv
import requests

# Load the environment variables
load_dotenv()


logger = logging.getLogger(__name__)


class PredictProtein3DStructureComponent(PandasTransformComponent):
	"""
	The PredictProtein3DStructureComponent is a component that takes
	in a dataframe and sends the sequences to the HuggingFace ESMFold Endpoint
	to predict the tertiary structures of the proteins.
	The component returns the dataframe with the predicted tertiary structures.
	"""

	def __init__(self):
		# pylint: disable=super-init-not-called
		self.hf_api_key = os.getenv("HF_API_KEY")
		self.hf_endpoint_url = os.getenv("HF_ENDPOINT_URL")

		if not self.hf_api_key or not self.hf_endpoint_url:
			raise Exception("environment variables not set.")

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""Perform the transformation on the dataframe."""

		# Ge the indices to predict
		indices_to_predict = dataframe[dataframe["pdb_string"] == ""].index

		# Predict the tertiary structures
		dataframe.loc[indices_to_predict, "pdb_string"] = \
			dataframe.loc[indices_to_predict, "sequence"].apply(
				self.predict_tertiary_structure)

		return dataframe

	def predict_tertiary_structure(self, sequence: str) -> str:
		"""Predict the tertiary structure of the protein sequence using
		HuggingFace ESMFold Endpoint.
		"""

		# Set the headers
		headers = {
			"Authorization": f"Bearer {self.hf_api_key}",
			"Content-Type": "application/json"
		}

		# Set the data
		data = {
			"inputs": sequence
		}

		# Send the request
		response = requests.post(self.hf_endpoint_url,
								headers=headers, json=data)

		# Check if the request was successful
		if response.status_code != 200:
			raise Exception(
					f"Request failed with status code {response.status_code} \
					and response {response.text}")

		# Return the pdb string
		return response.json()
