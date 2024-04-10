"""
The PeptideFeaturesComponent class is a component that takes in a dataframe, performs calculations on the sequence to generate new features and returns the dataframe with the new features added.
"""
import logging
import pandas as pd
import peptides
from fondant.component import PandasTransformComponent

# Set up logging
logger = logging.getLogger(__name__)

class PeptideFeaturesComponent(PandasTransformComponent):
	"""The PeptideFeaturesComponent class is a component that takes in a dataframe, performs calculations on the sequence to generate new features and returns the dataframe with the new features added."""

	def __init__(self, *_):
		pass

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""The transform method takes in a dataframe, generate new features and returns the dataframe with the new features added."""

		scales_list = ["z_scales", "vhse_scales", "t_scales", "st_scales"]
		for scale_method in scales_list:
			dataframe = self.calculate_scales(dataframe, scale_method)
		
		dataframe = self.calculate_aa_fractions(dataframe)	
		dataframe = self.calculate_mz(dataframe)

		logger.info(f"PeptideFeaturesComponent: features generated: {dataframe.columns.tolist()}")
		return dataframe
	
	def calculate_scales(self, dataframe: pd.DataFrame, scale_method: str) -> pd.DataFrame:
		"""
		Calculate the z-scales, vhse-scales, t-scales and st-scales of a peptide sequence.
		"""
		
		index = 1
		for sequence in dataframe["sequence"]:
			peptide = peptides.Peptide(sequence)
			if scale_method == "z_scales":
				scales = peptide.z_scales()
			elif scale_method == "vhse_scales":
				scales = peptide.vhse_scales()
			elif scale_method == "t_scales":
				scales = peptide.t_scales()
			elif scale_method == "st_scales":
				scales = peptide.st_scales()
			else:
				raise ValueError("Invalid scale method. Please choose from 'z_scales', 'vhse_scales', 't_scales' or 'st_scales'.")
			for i, scale in enumerate(scales):
				dataframe[f"{scale_method}_{i+index}"] = scale
		return dataframe
	
	def calculate_mz(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""
		Calculate the mass-to-charge ratio (m/z) of a peptide sequence.
		"""

		for sequence in dataframe["sequence"]:
			peptide = peptides.Peptide(sequence)
			mz = peptide.mz()
			dataframe["mz"] = mz

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
			dataframe[column_name] = dataframe["sequence"].apply(lambda x: sum(x.count(aa) for aa in amino_acids) / len(x))
		
		return dataframe
