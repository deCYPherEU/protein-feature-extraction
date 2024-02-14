import pandas as pd
import pyarrow as pa
from fondant.pipeline import Pipeline
from fondant.pipeline import lightweight_component
from fondant.component import PandasTransformComponent

MOCK_DATA_PATH_LOCAL = "./data/mock_data.parquet"
MOCK_DATA_PATH_FONDANT = MOCK_DATA_PATH_LOCAL[1:] # remove the dot

def generate_mock_data() -> None:
	data = {
		'sequence': [
			'MKTITLEVAVLAALLVLASATVA',
			'MKLITVLLLAVALAGVSKQIAG',
			'MKIFVALLVATLVWSKFIA',
			'MKALSKFNLSAKVNALKAASVNSA',
			'MKSLAISVNLSANVAISVNLSAASANS'
		],
		'name': ['Seq1', 'Seq2', 'Seq3', 'Seq4', 'Seq5']	
	}

	df = pd.DataFrame(data)
	df.to_parquet(MOCK_DATA_PATH_LOCAL, index=False)

# generate the mock data
generate_mock_data()

# create a new pipeline
pipeline = Pipeline(
	name="mock_data_pipeline",
	base_path=".artifacts",
	description="basic pipeline to generate a few features"
)

def load_all_rows(path: str) -> int:
	df = pd.read_parquet(path)
	return df.shape[0]


# read the dataset
dataset = pipeline.read(
	"load_from_parquet",
	arguments={
		"dataset_uri": MOCK_DATA_PATH_FONDANT,
		"n_rows_to_load": load_all_rows(MOCK_DATA_PATH_LOCAL)
	},
	produces={
		"sequence": pa.string()
	},
	cache=False
)


"""
@lightweight_component(
	produces={"sequence_length": pa.int64()}
)
class AddLengthFeature(PandasTransformComponent):
	def __init__(self):
		pass

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		print(dataframe.head())
		# dataframe["sequence_length"] = dataframe["sequence"].map(len)
		return dataframe

_ = dataset.apply(
	ref=AddLengthFeature,
	cache=False
)


"""

"""
dataset.write(
	"write_to_file",
	arguments={
		"path": "/data/mock_data-2.parquet",
		"format": "parquet"
	},
	consumes={
		"sequence": "sequence"
	},
)
"""

# fondant run local main.py --extra-volumes C:\Users\denis\Desktop\stage\fondant-example\data:/data