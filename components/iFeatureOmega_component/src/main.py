"""
The IFeatureOmegaComponent class is a component that generates new features using iFeatureOmega.
"""

import logging
import uuid
import pandas as pd
from fondant.component import PandasTransformComponent
import iFeatureOmega_CLI.iFeatureOmegaCLI as iFO

# Set up logging
logger = logging.getLogger(__name__)


class IFeatureOmegaComponent(PandasTransformComponent):
	"""The IFeatureOmegaComponent class is a component that generates new features using iFeatureOmega."""

	def __init__(self, descriptors: list):
		self.descriptors = descriptors

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""Perform the iFeatureOmega functions to generate new features and return the dataframe with the new features added."""

		# Get the sequence from the dataframe
		sequences = dataframe["sequence"].tolist()

		# Generate all features, only need one to get the column names
		all_features = self.generate_all_features_names(sequences[0])

		# Add the columns to the dataframe
		dataframe = pd.concat([dataframe, pd.DataFrame(columns=all_features)])

		# Generate the iFeatureOmega features
		dataframe = self.generate_ifeature_omega_values(sequences, dataframe)

		return dataframe

	def generate_ifeature_omega_values(self, sequences: list, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""Generate the iFeatureOmega features for the sequences and add them to the dataframe."""
		# for each descriptor, generate the values for one sequence
		for sequence in sequences:
			ifeature_omega_protein = self.create_ifo_protein(sequence)
			for descriptor in self.descriptors:
				ifeature_omega_protein.get_descriptor(descriptor)
				df_ifeature_protein = ifeature_omega_protein.encodings
				dataframe.loc[dataframe["sequence"] == sequence,
							df_ifeature_protein.columns] = df_ifeature_protein.values[0]

		return dataframe

	def create_ifo_protein(self, sequence: str) -> iFO.iProtein:
		"""Create an iFeatureOmega protein object from a sequence."""
		file_name = uuid.uuid4()
		file_path = f"/{file_name}.txt"
		with open(file_path, "w") as file:
			file.write(f">{file_name}\n")
			file.write(sequence)

		ifeature_omega_protein = iFO.iProtein(file_path)

		return ifeature_omega_protein

	def generate_all_features_names(self, sequence: str) -> list:
		"""Generate all the features names for the descriptors."""
		all_features = []

		single_protein = self.create_ifo_protein(sequence)

		for descriptor in self.descriptors:
			single_protein.get_descriptor(descriptor)
			df_ifeature_protein = single_protein.encodings
			all_features.extend(df_ifeature_protein.columns)

		return all_features
