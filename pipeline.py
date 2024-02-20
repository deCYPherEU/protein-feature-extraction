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

# apply the biopython component
biopython_dataset = dataset.apply(
    "./components/biopython_component",
)

# write the dataset to a parquet file
biopython_dataset.apply(
	"write_to_file",
	arguments={
		"path": "/data/export",
	},
	consumes={
		"sequence": pa.string(),
		"sequence_length": pa.int64(),
		"molecular_weight": pa.float64(),
		"aromaticity": pa.float64(),
		"isoelectric_point": pa.float64(),
		"instability_index": pa.float64(),
		"gravy": pa.float64(),
		"helix": pa.float64(),
		"turn": pa.float64(),
		"sheet": pa.float64(),
		"charge_at_ph7": pa.float64(),
		"charge_at_ph5": pa.float64(),
		"molar_extinction_coefficient_oxidized": pa.int64(),
		"molar_extinction_coefficient_reduced": pa.int64()
	}
)

# run the pipeline using your local path to the folder, this one is mine
# fondant run local pipeline.py --extra-volumes C:\Users\denis\Desktop\stage\protein-feature-extraction\data:/data