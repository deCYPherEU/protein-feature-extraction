"""
The DeepTMpred component predicts the number of transmembrane helices in a protein sequence using the DeepTMpred model.
"""
import logging
import json
import subprocess
import pandas as pd
from fondant.component import PandasTransformComponent

# Set up logging
logger = logging.getLogger(__name__)


class DeepTMpredComponent(PandasTransformComponent):
	"""The DeepTMpred component predicts the number of transmembrane helices in a protein sequence using the DeepTMpred model."""

	def __init__(self, *_):
		pass

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""Transform the dataframe by adding new features."""

		input_file = "all_sequences.fasta"
		output_file = "DeepTMpred/test.json"

		self.write_sequences_to_file(dataframe, input_file)
		self.run_deeptmpred_model(input_file, output_file)
		transmembrane_helices = self.read_and_parse_output(output_file)
		features = self.calculate_features(transmembrane_helices)
		dataframe = self.insert_features_into_dataframe(dataframe, features)

		return dataframe

	def write_sequences_to_file(self, dataframe: pd.DataFrame, input_file: str) -> None:
		"""Write sequences from dataframe to a file."""

		with open(input_file, 'w') as f:
			for index, row in dataframe.iterrows():
				f.write(f'>{row["sequence_id"]}\n{row["sequence"]}\n')

	def run_deeptmpred_model(self, input_file: str) -> None:
		"""Run the DeepTMpred model."""

		subprocess.run([
			'python',
			'DeepTMpred/tmh_main.py',
			'DeepTMpred/model_files/deepTMpred-b.pth',
			'DeepTMpred/model_files/orientaion-b.pth',
			input_file
		])

	def read_and_parse_output(self, output_file: str) -> list:
		"""Read and parse the output file."""

		with open(output_file, 'r') as f:
			output = f.read()
		output_dict = json.loads(output)
		transmembrane_helices = output_dict['test']['topo']
		return transmembrane_helices

	def calculate_features(self, transmembrane_helices: list) -> tuple:
		"""Calculate features based on the parsed output."""

		num_helices = len(transmembrane_helices)
		total_length = sum(end - start + 1 for start,
						end in transmembrane_helices)
		avg_length_total = total_length / num_helices
		biggest_length = max(end - start + 1 for start,
							end in transmembrane_helices)
		smallest_length = min(end - start + 1 for start,
							end in transmembrane_helices)
		return num_helices, total_length, avg_length_total, biggest_length, smallest_length

	def insert_features_into_dataframe(self, dataframe: pd.DataFrame, features: tuple) -> pd.DataFrame:
		"""Insert the new features into the dataframe."""

		num_helices, total_length, avg_length_total, biggest_length, smallest_length = features
		dataframe = dataframe.assign(
			tmh_num_helices=num_helices,
			tmh_total_length=total_length,
			tmh_avg_length_total=avg_length_total,
			tmh_biggest_length=biggest_length,
			tmh_smallest_length=smallest_length
		)
		return dataframe
