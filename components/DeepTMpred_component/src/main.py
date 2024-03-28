"""
The DeepTMpred component predicts the number of transmembrane helices in a protein sequence using the DeepTMpred model.
"""
import logging
import os
import time
import json
import subprocess
import pandas as pd
from fondant.component import PandasTransformComponent

# Set up logging
logger = logging.getLogger(__name__)


class DeepTMpredComponent(PandasTransformComponent):
	"""The DeepTMpred component predicts the number of transmembrane helices in a protein sequence using the DeepTMpred model."""

	def __init__(self, *_):
		self.columns = ['tmh_num_helices', 'tmh_total_length',
						'tmh_avg_length_total', 'tmh_biggest_length', 'tmh_smallest_length']

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""Transform the dataframe by adding new features."""

		input_file = "sequence.fasta"
		output_file = "test.json"

		self.create_columns(dataframe)

		for row in dataframe.itertuples():
			self.run_deeptmpred_model(
				input_file, row.sequence, row.sequence_checksum)
			transmembrane_helices = self.read_and_parse_output(
				input_file, output_file)
			features = self.calculate_features(transmembrane_helices)
			dataframe = self.insert_features_into_dataframe(
				dataframe, features, row.sequence_checksum)

		return dataframe

	def create_columns(self, dataframe: pd.DataFrame) -> None:
		"""Create new columns in the dataframe to store the new features."""

		for column in self.columns:
			dataframe[column] = None

	def run_deeptmpred_model(self, input_file: str, sequence: str, sequence_checksum: str) -> None:
		"""Run the DeepTMpred model."""

		with open(input_file, 'w') as f:
			f.write(f'>{sequence_checksum}\n{sequence}')

		subprocess.run([
			'python',
			'tmh_main.py',
			'model_files/deepTMpred-b.pth',
			'model_files/orientaion-b.pth',
			input_file
		])

	def read_and_parse_output(self, input_file: str, output_file: str) -> list:
		"""Read and parse the output file."""

		# wait until the output file is created.
		# Time is set to 3 seconds, because the model doesn't insert the values fast enough. 3 seconds is enough time to wait.
		while not os.path.exists(output_file):
			time.sleep(3)

		with open(output_file, 'r') as f:
			output = f.read()
		output_dict = json.loads(output)

		transmembrane_helices = output_dict[input_file]['topo']
		return transmembrane_helices

	def calculate_features(self, transmembrane_helices: dict) -> tuple:
		"""Calculate features based on the parsed output."""

		# check if empty
		if not transmembrane_helices:
			return 0, 0, 0.0, 0, 0

		tmh_num_helices = len(transmembrane_helices)
		tmh_total_length = sum(end - start + 1 for start,
							end in transmembrane_helices)
		tmh_avg_length_total = tmh_total_length / tmh_num_helices
		tmh_biggest_length = max(end - start + 1 for start,
								end in transmembrane_helices)
		tmh_smallest_length = min(end - start + 1 for start,
								end in transmembrane_helices)
		return tmh_num_helices, tmh_total_length, tmh_avg_length_total, tmh_biggest_length, tmh_smallest_length

	def insert_features_into_dataframe(self, dataframe: pd.DataFrame, features: tuple, sequence_checksum: str) -> pd.DataFrame:
		"""Insert the new features into the dataframe."""

		# Find the index where sequence_checksum matches in the dataframe
		index = dataframe[dataframe['sequence_checksum']
						== sequence_checksum].index[0]

		# Insert the new features into the dataframe at the corresponding index using the self.columns list
		for column, feature in zip(self.columns, features):
			dataframe.at[index, column] = feature

		return dataframe
