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

		# Get the sequence from the dataframe
		sequences = dataframe["sequence"].tolist()

		# Generate the iFeatureOmega features
		dataframe = self.generate_features(sequences)

		# add the sequences to the dataframe to the front
		dataframe.insert(0, "sequence", sequences)

		return dataframe

	def generate_features(self, sequences: list) -> pd.DataFrame:
		df_concat = pd.DataFrame()
		
		for sequence in sequences:
			with open(self.sequence_file, "w") as file:
				file.write(f">single_sequence\n")
				file.write(sequence)
			
			ifeatureO_protein = iFO.iProtein(self.sequence_file)
			df_single_protein = self.generate_descriptors_single_protein(ifeatureO_protein)
			df_single_protein.reset_index(drop=True, inplace=True)
			
			df_concat = pd.concat([df_concat, df_single_protein], axis=0)
			logger.info(f"{df_concat.head()}")
		
		df_concat.reset_index(drop=True, inplace=True)

		return df_concat

	def generate_descriptors_single_protein(self, single_protein: iFO.iProtein) -> pd.DataFrame:
		df_single_protein = pd.DataFrame()

		for descriptor in self.descriptors:
			single_protein.get_descriptor(descriptor)
			df_ifeature_protein = single_protein.encodings
			df_single_protein = pd.concat([df_single_protein, df_ifeature_protein], axis=1)
	
		return df_single_protein

