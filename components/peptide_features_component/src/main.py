"""
The PeptideFeaturesComponent uses the peptides package to generate new
features related to the amino acids in a protein sequence. These features
include physicochemical properties of amino acids (hydrophobicity, aliphaticity, ...)
and amino acid fractions and mass-to-charge ratio (m/z) of the peptide sequence.
"""
import logging
import pandas as pd
import peptides
from fondant.component import PandasTransformComponent

# Set up logging
logger = logging.getLogger(__name__)


class PeptideFeaturesComponent(PandasTransformComponent):
	"""The PeptideFeaturesComponent uses the peptides package to generate new
	features related to the amino acids in a protein sequence. These features
	include physicochemical properties of amino acids (hydrophobicity, aphiliaticity, ...)
	and amino acid fractions and mass-to-charge ratio (m/z) of the peptide sequence.
	"""

	def __init__(self, *_):
		pass

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""The transform method takes in a dataframe, generate new
		features and returns the dataframe with the new features added."""

		dataframe = self.calculate_aa_fractions(dataframe)
		dataframe = self.calculate_mz(dataframe)
		dataframe = self.calculate_z_scales(dataframe)

		logger.info(
			f"PeptideFeaturesComponent: features generated: {dataframe.columns.tolist()}")

		return dataframe

	def calculate_z_scales(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""
		Calculate the z-scales of peptide sequences.
		"""

		# z-scales are a set of 5 physicochemical properties of amino acids
		for i in range(5):
			dataframe[f"z_scale_{i+1}"] = dataframe["sequence"].apply(
				lambda sequence: peptides.Peptide(sequence).z_scales()[i])

		return dataframe

	def calculate_mz(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""
		Calculate the mass-to-charge ratio (m/z) of a peptide sequence.
		"""

		dataframe["mz"] = dataframe["sequence"].apply(
			lambda sequence: peptides.Peptide(sequence).mz())

		return dataframe

	def calculate_aa_fractions(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""
		Calculate the fractions of different categories of amino acids in the sequence.
		"""

		aa_categories = {
			"aliphatic": "AVLIG",
			"uncharged_polar": "STCNQ",
			"charged_polar": "STCNQHKR",
			"hydrophobic": "AILMFWVG",
			"positively_charged": "HKR",
			"negatively_charged": "DE",
			"sulfur_containing": "CM",
			"amide_containing": "NQ"
		}

		for category, amino_acids in aa_categories.items():
			column_name = f"{category}_aa_fraction"
			dataframe[column_name] = dataframe["sequence"].apply(
				lambda x: sum(x.count(aa) for aa in amino_acids) / len(x))

		return dataframe
