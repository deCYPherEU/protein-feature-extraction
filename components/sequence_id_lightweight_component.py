from fondant.pipeline import lightweight_component
from fondant.component import PandasTransformComponent
import pandas as pd
import pyarrow as pa


@lightweight_component(
	consumes={
		"sequence": pa.string()
	},
	produces={
		"sequence": pa.string(), 
		"sequence_id": pa.string(), 
	},
	extra_requires=["biopython==1.83"]
)
class SequenceIDComponent(PandasTransformComponent):
	""" Generates a unique sequence_id for each sequence in the input dataframe using the checksum of the sequence. """
	def __init__(self):
		"""
		Initializes the SequenceIDComponent class.
		"""
		pass

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""
		Compute the sequence_id for each sequence in the input dataframe.
		"""
		import Bio.SeqUtils.CheckSum

		dataframe["sequence_id"] = dataframe["sequence"].apply(lambda x: Bio.SeqUtils.CheckSum.crc64(x))

		return dataframe

