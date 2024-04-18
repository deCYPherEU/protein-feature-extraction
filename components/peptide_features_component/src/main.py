"""
The PeptideFeaturesComponent uses the peptides package to generate new
features related to the amino acids in a protein sequence. These features
include physicochemical properties of amino acids (hydrophobicity, aphiliaticity, ...)
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

		scales_list = ["z_scales", "vhse_scales", "t_scales", "st_scales"]
		dataframe = dataframe.apply(
			lambda row: self.calculate_scales_for_row(row, scales_list), axis=1)

		dataframe = self.calculate_aa_fractions(dataframe)
		dataframe = self.calculate_mz(dataframe)

		logger.info(
			f"PeptideFeaturesComponent: features generated: {dataframe.columns.tolist()}")
		return dataframe

	def calculate_scales(self, dataframe: pd.DataFrame, scale_method: str) -> pd.DataFrame:
		"""
		Calculate the z-scales, vhse-scales, t-scales and st-scales of a peptide sequence.
		"""

		index = 1
		dataframe[scale_method] = dataframe["sequence"].apply(
			lambda sequence: peptides.Peptide(sequence))
		dataframe[scale_method] = dataframe[scale_method].apply(
			lambda peptide: getattr(peptide, f"{scale_method}"))

		dataframe[[f"{scale_method}_{i+index}" for i in range(len(dataframe[scale_method][0]))]] = pd.DataFrame(
			dataframe[scale_method].tolist(), index=dataframe.index)
		dataframe.drop(columns=[scale_method], inplace=True)

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
