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

		dataframe["sequence_length"] = dataframe["sequence"].map(len)
		dataframe["molecular_weight"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).molecular_weight()
		)
		dataframe["aromaticity"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).aromaticity()
		)
		dataframe["isoelectric_point"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).isoelectric_point()
		)
		dataframe["instability_index"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).instability_index()
		)
		dataframe["gravy"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).gravy()
		)
		dataframe["helix"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).secondary_structure_fraction()[0]
		)
		dataframe["turn"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).secondary_structure_fraction()[1]
		)
		dataframe["sheet"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).secondary_structure_fraction()[2]
		)
		dataframe["charge_at_ph7"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).charge_at_pH(7.0)
		)
		dataframe["charge_at_ph5"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).charge_at_pH(5.0)
		)
		dataframe["molar_extinction_coefficient_oxidized"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).molar_extinction_coefficient()[1]
		)
		dataframe["molar_extinction_coefficient_reduced"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).molar_extinction_coefficient()[0]
		)

		logger.info(f"BiopythonComponent: features generated: {dataframe.columns.tolist()}")
		return dataframe
