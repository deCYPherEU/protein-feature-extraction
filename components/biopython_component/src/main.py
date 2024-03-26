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

		sequence_analysis = dataframe["sequence"].apply(ProteinAnalysis)

		dataframe["sequence_length"] = sequence_analysis.apply(
			lambda x: x.length)
		dataframe["molecular_weight"] = sequence_analysis.apply(
			lambda x: x.molecular_weight())
		dataframe["aromaticity"] = sequence_analysis.apply(
			lambda x: x.aromaticity())
		dataframe["isoelectric_point"] = sequence_analysis.apply(
			lambda x: x.isoelectric_point())
		dataframe["instability_index"] = sequence_analysis.apply(
			lambda x: x.instability_index())
		dataframe["flexibility_max"] = sequence_analysis.apply(lambda x: max(x.flexibility()))
		dataframe["flexibility_min"] = sequence_analysis.apply(lambda x: min(x.flexibility()))
		dataframe["flexibility_mean"] = sequence_analysis.apply(lambda x: sum(x.flexibility()) / len(x.flexibility()))
		dataframe["gravy"] = sequence_analysis.apply(lambda x: x.gravy())
		dataframe["helix"] = sequence_analysis.apply(
			lambda x: x.secondary_structure_fraction()[0])
		dataframe["turn"] = sequence_analysis.apply(
			lambda x: x.secondary_structure_fraction()[1])
		dataframe["sheet"] = sequence_analysis.apply(
			lambda x: x.secondary_structure_fraction()[2])
		dataframe["molar_extinction_coefficient_oxidized"] = sequence_analysis.apply(
			lambda x: x.molar_extinction_coefficient()[0])
		dataframe["molar_extinction_coefficient_reduced"] = sequence_analysis.apply(
			lambda x: x.molar_extinction_coefficient()[1])
		dataframe["helix"] = sequence_analysis.apply(lambda x: x.secondary_structure_fraction()[0])
		dataframe["turn"] = sequence_analysis.apply(lambda x: x.secondary_structure_fraction()[1])
		dataframe["sheet"] = sequence_analysis.apply(lambda x: x.secondary_structure_fraction()[2])
		dataframe["charge_at_ph3"] = sequence_analysis.apply(lambda x: x.charge_at_pH(3.0))
		dataframe["charge_at_ph5"] = sequence_analysis.apply(lambda x: x.charge_at_pH(5.0))
		dataframe["charge_at_ph7"] = sequence_analysis.apply(lambda x: x.charge_at_pH(7.0))
		dataframe["charge_at_ph9"] = sequence_analysis.apply(lambda x: x.charge_at_pH(9.0))

		return dataframe
