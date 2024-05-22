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


logger = logging.getLogger(__name__)


class PeptideFeaturesComponent(PandasTransformComponent):
	"""The PeptideFeaturesComponent uses the peptides package to generate new
	features related to the amino acids in a protein sequence. These features
	include physicochemical properties of amino acids (hydrophobicity, aphiliaticity, ...)
	and amino acid fractions and mass-to-charge ratio (m/z) of the peptide sequence.
	"""

	def __init__(self, *_):
		# pylint: disable=super-init-not-called
		pass

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""The transform method takes in a dataframe, generates new
		features, and returns the dataframe with the new features added."""

		dataframe = self.calculate_aa_fractions(dataframe)
		dataframe["mz"] = dataframe["sequence"].apply(
			lambda sequence: peptides.Peptide(sequence).mz())

		z_scales = [peptides.Peptide(sequence).z_scales() for sequence in dataframe["sequence"]]

		for i in range(5):
			dataframe[f"z_scale_{i+1}"] = [z[i] for z in z_scales]

		return dataframe


	def calculate_aa_fractions(self, dataframe: pd.DataFrame) -> pd.DataFrame:  # pylint: disable=no-self-use
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
