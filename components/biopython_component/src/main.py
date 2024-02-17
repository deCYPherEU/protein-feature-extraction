"""
The BiopythonComponent class is a component that takes in a dataframe, performs the Biopython functions to generate new features and returns the dataframe with the new features added.
"""
import logging
import os
import pandas as pd
from fondant.component import PandasTransformComponent
import pyarrow as pa
import importlib.util

# Set up logging
logger = logging.getLogger(__name__)
FEATURES_GENERATED_OBJECT = {}

# This is used to import the constants.py file, so that I can use the FEATURES_GENERATED_OBJECT. It's rather difficult to import a file from a different directory in a fondant component. This is a workaround. If there is an easier way to do this, I'll be happy to hear it.
constants_path = os.path.abspath(os.path.join(os.path.dirname(__name__), "../../../components/constants.py"))
if os.path.exists(constants_path):
	# Define a new module name
	module_name = "custom_constants_module"
	# Define a new module spec
	spec = importlib.util.spec_from_file_location(module_name, constants_path)
	# Create the module
	constants_module = importlib.util.module_from_spec(spec)
	# Load the module
	spec.loader.exec_module(constants_module)
	# Access FEATURES_GENERATED_OBJECT from the module
	FEATURES_GENERATED_OBJECT = constants_module.FEATURES_GENERATED_OBJECT


class BiopythonComponent(PandasTransformComponent):
	"""The BiopythonComponent class is a component that takes in a dataframe, performs the Biopython functions to generate new features and returns the dataframe with the new features added."""

	def __init__(self, *_):
		pass

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""The transform method takes in a dataframe, performs the Biopython functions to generate new features and returns the dataframe with the new features added."""
		dataframe = self.sequence_length(dataframe)
		dataframe = self.molecular_weight(dataframe)
		dataframe = self.aromaticity(dataframe)
		dataframe = self.isoelectric_point(dataframe)
		dataframe = self.instability_index(dataframe)
		dataframe = self.gravy(dataframe)
		dataframe = self.flexibility(dataframe)
		dataframe = self.helix(dataframe)
		dataframe = self.turn(dataframe)
		dataframe = self.sheet(dataframe)
		dataframe = self.charge_at_pH(dataframe)
		dataframe = self.molar_extinction_coefficient_oxidized(dataframe)
		dataframe = self.molar_extinction_coefficient_reduced(dataframe)
		logger.info(f"BiopythonComponent: features generated: {FEATURES_GENERATED_OBJECT}")
		return dataframe

	def sequence_length(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		dataframe["sequence_length"] = dataframe["sequence"].map(len)
		FEATURES_GENERATED_OBJECT["sequence_length"] = pa.int64()
		return dataframe
	
	def molecular_weight(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		from Bio.SeqUtils.ProtParam import ProteinAnalysis
		dataframe["molecular_weight"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).molecular_weight()
		)
		FEATURES_GENERATED_OBJECT["molecular_weight"] = pa.float64()
		return dataframe

	def aromaticity(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		from Bio.SeqUtils.ProtParam import ProteinAnalysis
		dataframe["aromaticity"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).aromaticity()
		)
		FEATURES_GENERATED_OBJECT["aromaticity"] = pa.float64()
		return dataframe

	def isoelectric_point(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		from Bio.SeqUtils.ProtParam import ProteinAnalysis
		dataframe["isoelectric_point"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).isoelectric_point()
		)
		FEATURES_GENERATED_OBJECT["isoelectric_point"] = pa.float64()
		return dataframe
	
	def instability_index(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		from Bio.SeqUtils.ProtParam import ProteinAnalysis
		dataframe["instability_index"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).instability_index()
		)
		FEATURES_GENERATED_OBJECT["instability_index"] = pa.float64()
		return dataframe
	
	def gravy(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		from Bio.SeqUtils.ProtParam import ProteinAnalysis
		dataframe["gravy"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).gravy()
		)
		FEATURES_GENERATED_OBJECT["gravy"] = pa.float64()
		return dataframe
	
	def flexibility(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		from Bio.SeqUtils.ProtParam import ProteinAnalysis
		dataframe["flexibility"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).flexibility()
		)
		FEATURES_GENERATED_OBJECT["flexibility"] = pa.float64()
		return dataframe
	
	def helix(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		from Bio.SeqUtils.ProtParam import ProteinAnalysis
		dataframe["helix"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).secondary_structure_fraction()[0]
		)
		FEATURES_GENERATED_OBJECT["helix"] = pa.float64()
		return dataframe
	
	def turn(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		from Bio.SeqUtils.ProtParam import ProteinAnalysis
		dataframe["turn"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).secondary_structure_fraction()[1]
		)
		FEATURES_GENERATED_OBJECT["turn"] = pa.float64()
		return dataframe
	
	def sheet(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		from Bio.SeqUtils.ProtParam import ProteinAnalysis
		dataframe["sheet"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).secondary_structure_fraction()[2]
		)
		FEATURES_GENERATED_OBJECT["sheet"] = pa.float64()
		return dataframe
	
	def charge_at_pH(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		from Bio.SeqUtils.ProtParam import ProteinAnalysis
		dataframe["charge_at_pH"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).charge_at_pH(7.0)
		)
		FEATURES_GENERATED_OBJECT["charge_at_pH"] = pa.float64()
		return dataframe

	def molar_extinction_coefficient_oxidized(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		from Bio.SeqUtils.ProtParam import ProteinAnalysis
		dataframe["molar_extinction_coefficient_oxidized"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).molar_extinction_coefficient()[1]
		)
		FEATURES_GENERATED_OBJECT["molar_extinction_coefficient_oxidized"] = pa.float64()
		return dataframe
	
	def molar_extinction_coefficient_reduced(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		from Bio.SeqUtils.ProtParam import ProteinAnalysis
		dataframe["molar_extinction_coefficient_reduced"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).molar_extinction_coefficient()[0]
		)
		FEATURES_GENERATED_OBJECT["molar_extinction_coefficient_reduced"] = pa.float64()
		return dataframe
	
