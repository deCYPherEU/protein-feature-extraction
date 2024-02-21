import logging
import pandas as pd
from fondant.component import PandasTransformComponent
import iFeatureOmega_CLI.iFeatureOmegaCLI as iFO

# Set up logging
logger = logging.getLogger(__name__)

class IFeatureOmegaComponent(PandasTransformComponent):
	"""The IFeatureOmegaComponent class is a component that generates new features using iFeatureOmega."""

	def __init__(self, *_):
		self.descriptors = ["AAC", "GAAC", "Moran", "Geary", "NMBroto", "APAAC"]
		self.sequence_file = "/single_protein.txt"

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:

		dataframe = self.generate_features(dataframe["sequence"].tolist(), dataframe)
		dataframe = self.modify_features_to_string(dataframe)
		
		return dataframe

	def generate_features(self, sequences: list, dataframe: pd.DataFrame) -> pd.DataFrame:
		list_of_dfs = []
		for sequence in sequences:
			with open(self.sequence_file, "w") as file:
				file.write(f">single_sequence\n")
				file.write(sequence)
			
			ifeatureO_protein = iFO.iProtein(self.sequence_file)
			df_single_protein = self.generate_descriptors_single_protein(ifeatureO_protein, sequence)
			df_single_protein.reset_index(drop=True, inplace=True)

			list_of_dfs.append(df_single_protein)
			logger.info(f"{list_of_dfs}")
		
		dataframe = pd.concat(list_of_dfs, axis=0)

		return dataframe

	def generate_descriptors_single_protein(self, single_protein: iFO.iProtein, sequence: str) -> pd.DataFrame:
		df_single_protein = pd.DataFrame()

		for descriptor in self.descriptors:
			single_protein.get_descriptor(descriptor)
			df_ifeature_protein = single_protein.encodings
			df_single_protein = pd.concat([df_single_protein, df_ifeature_protein], axis=1)
	
		# Add the sequence to the dataframe
		df_single_protein["sequence"] = sequence
		return df_single_protein

	def modify_features_to_string(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""
		Converts all of the features into a single column as an object and then as a string.
		This is then saved to the feature named "iFeatureOmega_features" and the sequence is also saved to the dataframe.
		This is a workaround to save all of the features.
		"""
		# Exclude the sequence column
		df_ifeature_omega_features = dataframe.copy()
		df_ifeature_omega_features.drop(columns=["sequence"], inplace=True)

		# Convert each feature to a dictionary
		df_ifeature_omega_features["features_as_dict"] = df_ifeature_omega_features.apply(lambda x: x.to_dict(), axis=1)

		# Convert the dictionary of features to a string
		df_ifeature_omega_features["iFeatureOmega_features"] = df_ifeature_omega_features["features_as_dict"].apply(str)

		# Rearrange columns and include the sequence column
		df_ifeature_omega_features["sequence"] = dataframe["sequence"]
		df_ifeature_omega_features = df_ifeature_omega_features[["sequence", "iFeatureOmega_features"]]

		return df_ifeature_omega_features
