import pandas as pd
import pyarrow as pa
from fondant.component import PandasTransformComponent
from fondant.pipeline import lightweight_component

@lightweight_component(
	produces={"gc_content": pa.float32()}
)
class GCContentComponent(PandasTransformComponent):
	def __init__(self):
		pass

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		dataframe["gc_content"] = dataframe["sequence"].map(
			lambda x: (x.count("G") + x.count("C")) / len(x)
		)
		return dataframe


# Sequence length component
@lightweight_component(
	produces={"sequence_length": pa.int64()}
)
class SequenceLengthComponent(PandasTransformComponent):
	def __init__(self):
		pass

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		dataframe["sequence_length"] = dataframe["sequence"].map(len)
		return dataframe


# Molecular weight component
@lightweight_component(
	produces={"molecular_weight": pa.float64()},
	extra_requires=["biopython"]
)
class MolecularWeightComponent(PandasTransformComponent):
	def __init__(self):
		pass

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		from Bio.SeqUtils.ProtParam import ProteinAnalysis
		dataframe["molecular_weight"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).molecular_weight()
		)

		print(dataframe)
		return dataframe


# Aromaticity component
@lightweight_component(
	produces={"aromaticity": pa.float64()},
	extra_requires=["biopython"]
)
class AromaticityComponent(PandasTransformComponent):
	def __init__(self):
		pass

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		from Bio.SeqUtils.ProtParam import ProteinAnalysis
		dataframe["aromaticity"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).aromaticity()
		)

		print(dataframe)
		return dataframe


# Isoelectric point component
@lightweight_component(
	produces={"isoelectric_point": pa.float64()},
	extra_requires=["biopython"]
)
class IsoelectricPointComponent(PandasTransformComponent):
	def __init__(self):
		pass

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		from Bio.SeqUtils.ProtParam import ProteinAnalysis
		dataframe["isoelectric_point"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).isoelectric_point()
		)

		print(dataframe)
		return dataframe


# Instability index component
@lightweight_component(
	produces={"instability_index": pa.float64()},
	extra_requires=["biopython"]
)
class InstabilityIndexComponent(PandasTransformComponent):
	def __init__(self):
		pass

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		from Bio.SeqUtils.ProtParam import ProteinAnalysis
		dataframe["instability_index"] = dataframe["sequence"].map(
			lambda x: ProteinAnalysis(x).instability_index()
		)

		print(dataframe)
		return dataframe

