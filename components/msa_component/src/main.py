"""
The MSA Component will take in a dataframe with a column of sequences and return a dataframe with the MSA sequences as a new column
"""
import logging
import subprocess
import pandas as pd
from fondant.component import PandasTransformComponent

# Set up logging
logger = logging.getLogger(__name__)


class MSAComponent(PandasTransformComponent):
	"""The MSA Component will take in a dataframe with a column of sequences and return a dataframe with the MSA sequences as a new column"""

	def __init__(self, *_):
		pass

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""The transform method will take in a dataframe with a column of sequences and return a dataframe with the MSA sequences as a new column"""

		msa_file_content = self.execute_clustalo_cmd(dataframe)
		dataframe = self.add_msa_sequences_to_dataframe(
			msa_file_content, dataframe)

		return dataframe

	def execute_clustalo_cmd(self, dataframe: pd.DataFrame) -> str:
		"""Run Clustalo on the input file and return the content of the msa file"""

		input_file = "all_sequences.fasta"
		output_file = "msa.fasta"

		# create output file
		with open(output_file, "w") as f:
			f.write("")

		for index, row in dataframe.iterrows():
			with open(input_file, "a") as f:
				f.write(f">{row['sequence_id']}\n{row['sequence']}\n")

		subprocess.run(
			f'clustalo -t Protein -i {input_file} -o {output_file} --force', shell=True)

		# get content of output file
		with open(output_file, "r") as f:
			content = f.read()

		return content

	def add_msa_sequences_to_dataframe(self, msa_file_content: str, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""Read the MSA file and add the MSA sequences to the dataframe"""

		entries = msa_file_content.split('>')
		msa_dict = {}

		for entry in entries:
			if entry == "":
				continue
			lines = entry.split('\n')
			sequence_id = lines[0]
			msa_sequence = lines[1]
			msa_dict[sequence_id] = msa_sequence

		dataframe['msa_sequence'] = dataframe['sequence_id'].map(msa_dict)

		return dataframe
