"""
The GenerateProteinSequenceChecksumComponent is a component that takes in a dataframe and applies a checksum to the sequence column. The checksum is then added as a new column to the dataframe.
"""
import logging
import pandas as pd
from fondant.component import PandasTransformComponent
from Bio.SeqUtils.CheckSum import crc64

# Set up logging
logger = logging.getLogger(__name__)

class GenerateProteinSequenceChecksumComponent(PandasTransformComponent):
	"""The GenerateProteinSequenceChecksumComponent is a component that takes in a dataframe and applies a checksum to the sequence column. The checksum is then added as a new column to the dataframe."""

	def __init__(self, *_):
		pass

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""Apply a CRC64 checksum to each sequence and store the result in a new column."""

		dataframe['sequence_checksum'] = dataframe['sequence'].apply(crc64)

		return dataframe
