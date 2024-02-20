import logging
import os
import pandas as pd
import subprocess
from fondant.component import PandasTransformComponent

# Set up logging
logger = logging.getLogger(__name__)

class IFeatureComponent(PandasTransformComponent):
	"""The IFeatureComponent class is a component that generates new features using iFeature."""

	ENCODING_CSV = "/iFeature/encoding.csv"
	ENCODING_TSV = "/iFeature/encoding.tsv"
	TEMP_FOLDER = "/iFeature/temp_folder"
	SEQUENCE_FILE = "/iFeature/proteins.txt"

	def __init__(self):
		self.script_dir = os.path.dirname(os.path.realpath(__file__))
		self.ENCODING_CSV = os.path.join(self.script_dir, "encoding.csv")
		self.ENCODING_TSV = os.path.join(self.script_dir, "encoding.tsv")
		self.TEMP_FOLDER = os.path.join(self.script_dir, "iFeature", "temp_folder")
		self.SEQUENCE_FILE = os.path.join(self.script_dir, "iFeature", "proteins.txt")

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""Generates new features using iFeature and returns the dataframe with the new features added."""
		features = ["AAC", "GAAC", "Moran", "Geary", "NMBroto", "APAAC"]

		temp_dataframe = self.generate_features(dataframe["sequence"], features)
		logger.info(len(temp_dataframe.columns))

		return dataframe

	def generate_features(self, sequences: pd.Series, features: list) -> pd.DataFrame:
		"""Generates new features for the given sequences using iFeature."""
		# Create a temporary folder to store intermediate files
		os.makedirs(self.TEMP_FOLDER, exist_ok=True)

		# Create the sequence file using the provided sequences
		self.create_sequence_file(sequences)

		# Generate features for each sequence and aggregate them
		df_main = pd.DataFrame()
		
		for i in range(len(sequences)):
			df = self.modify_columns_ifeature(f"{self.TEMP_FOLDER}/temp_seq_{i}.txt", features)
			df_main = pd.concat([df_main, df])
		
		return df_main

	def create_sequence_file(self, sequences: pd.Series) -> None:
		"""Creates the sequence file in FASTA format using the provided sequences."""
		with open(self.SEQUENCE_FILE, "w") as f:
			for i, sequence in sequences.items():
				f.write(f">{i}\n{sequence}\n")
		
		# Create the sequences files in the temp folder
		with open(self.SEQUENCE_FILE, "r") as f:
			for i in range(len(sequences)):
				with open(f"{self.TEMP_FOLDER}/temp_seq_{i}.txt", "w") as f:
					f.write(f">{i}\n{sequences[i]}\n")

	def execute_ifeature(self, sequence_file: str, feature_type: str) -> pd.DataFrame:
		"""Executes iFeature for the given feature type and returns the dataframe with the new features."""
		process = subprocess.Popen(["python", "./iFeature/iFeature.py", "--file", sequence_file, "--type", feature_type])

		# Wait for the process to finish
		process.wait()

		# Check if encoding.tsv file is generated
		if not os.path.exists(self.ENCODING_TSV):
			raise FileNotFoundError(f"{self.ENCODING_TSV} not found. iFeature execution failed.")

		# Convert TSV to CSV
		with open(self.ENCODING_TSV, "r") as f:
			data = f.read().replace("\t", ",")
		with open(self.ENCODING_CSV, "w") as f:
			f.write(data)
			logger.info(f"Converted {self.ENCODING_TSV} to {self.ENCODING_CSV}")

		# Open the output file in a dataframe
		logger.info(f"Reading {self.ENCODING_CSV}")
		df = pd.read_csv(self.ENCODING_CSV)

		# Remove the "#" feature from the dataframe (first column)
		df = df.iloc[:, 1:]

		# Rename the feature columns to include the feature type prefix
		df.columns = [f"{feature_type}_{col}" for col in df.columns]

		return df

	def modify_columns_ifeature(self, sequence_file: str, features: list) -> pd.DataFrame:
		"""Modifies the columns for the iFeature features, normalizes them, handles missing values, and aggregates them."""
		df_main = pd.DataFrame()

		# Execute iFeature for each feature type and concatenate the results
		for feature in features:
			df_feature = self.execute_ifeature(sequence_file, feature)
			df_main = pd.concat([df_main, df_feature], axis=1)
		
		# Read the sequence from the input file
		with open(sequence_file, "r") as f:
			lines = f.readlines()
			sequence = "".join([line.strip() for line in lines[1:]])
		
		# Create a DataFrame for the sequence
		df_sequence = pd.DataFrame({"sequence": [sequence]})
		
		# Add the sequence DataFrame to the main DataFrame
		df_main = pd.concat([df_sequence, df_main], axis=1)

		# Normalize features by dividing each feature value by the length of the protein sequence
		seq_length = len(sequence)
		for col in df_main.columns[1:]:  # Exclude the sequence column
			df_main[col] /= seq_length

		# Handling missing values by placing them in their own category
		df_main.fillna(value="missing", inplace=True)

		# Feature aggregation: take the mean of the normalized feature values across all positions
		df_agg = df_main.groupby("sequence").mean().reset_index()

		return df_agg
