import pyarrow as pa
from fondant.pipeline import Pipeline
from config import MOCK_DATA_PATH_FONDANT

# create a new pipeline
pipeline = Pipeline(
	name="feature_extraction_pipeline",
	base_path=".fondant",
	description="A pipeline to extract features from protein sequences."
)

# read the dataset
dataset = pipeline.read(
	"load_from_parquet",
	arguments={
		"dataset_uri": MOCK_DATA_PATH_FONDANT,
	},
	produces={
		"sequence": pa.string()
	}
)

# apply the containerized components to the dataset
dataset = dataset.apply(
	"./components/iFeatureOmega_component"
)

"""
# write the dataset to a parquet file
dataset.apply(
	"write_to_file",
	arguments={
		"path": "/data/export",
	},
	consumes={
		"sequence": pa.string(),
		"iFeatureOmega_features": pa.string()
	}
)
"""

# run the pipeline using your local path to the folder, this one is mine
# fondant run local pipeline.py --extra-volumes C:\Users\denis\Desktop\stage\protein-feature-extraction\data:/data