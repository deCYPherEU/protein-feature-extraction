"""
The DeepTMpred component predicts the number of transmembrane helices
in a protein sequence using the DeepTMpred model.
"""
import logging
from typing import Any, Dict, Tuple

import pandas as pd
from fondant.component import PandasTransformComponent
from .run_deeptm import deeptmpred


logger = logging.getLogger(__name__)


class DeepTMpredComponent(PandasTransformComponent):
	"""
	The DeepTMpred component predicts the number of transmembrane helices
	in a protein sequence using the DeepTMpred model.
	"""

	def __init__(self, *_):
		# pylint: disable=super-init-not-called
		self.columns = ['tmh_num_helices', 'tmh_total_length',
						'tmh_avg_length_total', 'tmh_max_length', 'tmh_min_length']

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""Transform the dataframe by adding new features."""

		input_file = "sequence.fasta"

		self.create_columns(dataframe)

		for index, row in dataframe.iterrows():  # pylint: disable=unused-variable
			transmembrane_helices = self.run_deeptmpred_model(
				input_file, row.sequence_checksum, row.sequence)
			features = self.calculate_features(transmembrane_helices)
			dataframe = self.insert_features_into_dataframe(
				dataframe, features, row.sequence_checksum)

		return dataframe

	def create_columns(self, dataframe: pd.DataFrame) -> None:
		"""Create new columns in the dataframe to store the new features."""

		for column in self.columns:
			dataframe[column] = None

	def run_deeptmpred_model(self, input_file: str, sequence_checksum: str, sequence: str) -> Dict[str, Any]:  # pylint: disable=no-self-use,line-too-long
		"""Run the DeepTMpred model."""

		with open(input_file, 'w') as f:
			f.write(f'>{sequence_checksum}\n{sequence}')

		deeptmpred_topo = deeptmpred(
			input_file, "model_files/deepTMpred-b.pth", "model_files/orientaion-b.pth")

		return deeptmpred_topo

	def calculate_features(self, transmembrane_helices: Dict) -> Tuple[int, int, int, int, int]:  # pylint: disable=no-self-use,line-too-long
		"""Calculate features based on the parsed output."""

		# check if empty
		if not transmembrane_helices:
			return None, None, None, None, None

		tmh_num_helices = len(transmembrane_helices)
		tmh_total_length = sum(end - start + 1 for start,
							end in transmembrane_helices)
		tmh_avg_length_total = tmh_total_length / tmh_num_helices
		tmh_biggest_length = max(end - start + 1 for start,
								end in transmembrane_helices)
		tmh_smallest_length = min(end - start + 1 for start,
								end in transmembrane_helices)
		return tmh_num_helices, tmh_total_length, tmh_avg_length_total, \
			tmh_biggest_length, tmh_smallest_length

	def insert_features_into_dataframe(self, dataframe: pd.DataFrame, features: tuple, sequence_checksum: str) -> pd.DataFrame:  # pylint: disable=line-too-long
		"""Insert the new features into the dataframe."""

		# Find the index where sequence_checksum matches in the dataframe
		index = dataframe[dataframe['sequence_checksum']
						== sequence_checksum].index[0]

		# Insert the features into the dataframe
		for column, feature in zip(self.columns, features):
			dataframe.at[index, column] = feature

		return dataframe
