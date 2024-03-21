"""
The BiopythonComponent class is a component that takes in a dataframe, performs the Biopython functions to generate new features and returns the dataframe with the new features added.
"""
import logging
import pandas as pd
from fondant.component import PandasTransformComponent
from Bio.SeqUtils.ProtParam import ProteinAnalysis

# Set up logging
logger = logging.getLogger(__name__)

		
class BiopythonComponent(PandasTransformComponent):
	"""The BiopythonComponent class is a component that takes in a dataframe, performs the Biopython functions to generate new features and returns the dataframe with the new features added."""

	def __init__(self, *_):
		pass

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""The transform method takes in a dataframe, performs the Biopython functions to generate new features and returns the dataframe with the new features added."""

		def analyze_protein(sequence: str) -> dict:
			"""The analyze_protein function takes in a protein sequence and returns a dictionary of the calculated protein features."""
			try:
				analyzed_protein = ProteinAnalysis(sequence)
				features = {
					"sequence_length": analyzed_protein.length,
					"molecular_weight": analyzed_protein.molecular_weight(),
					"aromaticity": analyzed_protein.aromaticity(),
					"isoelectric_point": analyzed_protein.isoelectric_point(),
					"instability_index": analyzed_protein.instability_index(),
					"gravy": analyzed_protein.gravy(),
					"helix": analyzed_protein.secondary_structure_fraction()[0],
					"turn": analyzed_protein.secondary_structure_fraction()[1],
					"sheet": analyzed_protein.secondary_structure_fraction()[2],
					"charge_at_pH_5": analyzed_protein.charge_at_pH(5),
					"charge_at_pH_7": analyzed_protein.charge_at_pH(7),
					# "molar_extinction_coefficient_oxidized": analyze_protein.molar_extinction_coefficient()[0],
					# "molar_extinction_coefficient_reduced": analyze_protein.molar_extinction_coefficient()[1],
				}
				return features
			except Exception as e:
				logger.error(f"Error analyzing protein sequence: {e}")
				return {
					"sequence_length": None,
					"molecular_weight": None,
					"aromaticity": None,
					"isoelectric_point": None,
					"instability_index": None,
					"gravy": None,
					"helix": None,
					"turn": None,
					"sheet": None,
					"charge_at_pH_5": None,
					"charge_at_pH_7": None,
					# "molar_extinction_coefficient_oxidized": None,
					# "molar_extinction_coefficient_reduced": None,
				}
		
		# Apply the analyze_protein function to the sequence column
		dataframe = dataframe.assign(**dataframe["sequence"].apply(analyze_protein).apply(pd.Series))
		logger.info(dataframe.head())
		return dataframe
			