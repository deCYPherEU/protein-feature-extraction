"""
The ifeatpro component class is a component that takes in a dataframe, performs the ifeatpro functions to generate new features and returns the dataframe with the new features added.
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


class IfeatproComponent(PandasTransformComponent):
	"""The ifeatpro component class is a component that takes in a dataframe, performs the ifeatpro functions to generate new features and returns the dataframe with the new features added."""

	def __init__(self, *_):
		pass

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		output_directory = "/features_folder"
		for index, row in dataframe.iterrows():
			sequence = row["sequence"]
			features_df = self.generate_features_using_ifeatpro(sequence, output_directory)
			dataframe = pd.concat([dataframe, features_df], axis=1)

		# Cleanup
		self.cleanup(dataframe)

		logger.info(f"ifeatpro component: features generated: {FEATURES_GENERATED_OBJECT}")
		return dataframe

	def generate_features_using_ifeatpro(self, sequence:str, output_directory: str) -> pd.DataFrame:
		from ifeatpro.features import get_all_features
		tmp_fasta_file = "current_sequence.fasta"
		sequence_id = "current_sequence_id"
		output_directory = "./features_folder"

		with open(tmp_fasta_file, "w") as f:
			f.write(f">{sequence_id}\n")
			f.write(sequence)
			f.write("\n")
		
		logger.info(f"fasta file created: {tmp_fasta_file}")

		# Generate features using iFeatPro
		get_all_features(tmp_fasta_file, output_directory)

		# Remove the tpc.csv file (if it exists), it doesn't generate anything good
		tpc_file = os.path.join(output_directory, "tpc.csv")
		if os.path.exists(tpc_file):
			os.remove(tpc_file)

		# Combine features into a DataFrame
		features_df = self.combine_features(output_directory, sequence_id)  # Pass the sequence identifier

		return features_df
	

	def combine_features(self, output_directory: str, sequence_id: str) -> pd.DataFrame:
		combined_features = pd.DataFrame()
		for filename in os.listdir(output_directory):
			if filename.endswith(".csv"):
				feature_name = os.path.splitext(filename)[0]
				df = pd.read_csv(os.path.join(output_directory, filename), header=None)
				# Exclude the first column (sequence identifier)
				df = df.drop(columns=0)
				df.columns = [f"{feature_name}_{i+1}" for i in range(df.shape[1])]
				combined_features = pd.concat([combined_features, df], axis=1)
		# Insert sequence identifier as the first column
		combined_features.insert(0, "sequence", sequence_id)
		return combined_features


	def cleanup(self, dataframe: pd.DataFrame):
		# Remove the sequence column, because it's already in the dataframe
		dataframe = dataframe.drop(columns="sequence")

		# Add the features generated to the FEATURES_GENERATED_OBJECT
		for column in dataframe.columns:
			FEATURES_GENERATED_OBJECT[column] = pa.float64()
