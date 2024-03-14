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

# apply the cloud pdb component
_ = dataset.apply(
	"./components/cloud_pdb_component",
).apply(
	"./components/biopython_component"
).apply(
	"./components/iFeatureOmega_component",
	# currently forcing the number of rows to 5, but there needs to be a better way to do this, see readme for more info
	input_partition_rows=5,
	# change the descriptors? => change the features of the yaml file 
	arguments={
		"descriptors": ["AAC", "CTDC", "CTDT"]
	}
)

"""
# write the dataset
_ = dataset.write(
	"write_to_file",
	arguments={
		"path": "/data/export/",
	}
)
"""

# run the pipeline using your local path to the folder, this one is mine
# fondant run local pipeline.py --extra-volumes C:\Users\denis\Desktop\stage\protein-feature-extraction\data:/data