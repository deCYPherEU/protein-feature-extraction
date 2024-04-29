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

_ = dataset.apply(
	"./components/biopython_component"
).apply(
	"./components/generate_protein_sequence_checksum_component"
).apply(
	"./components/iFeatureOmega_component",
	# currently forcing the number of rows to 5, but there needs to be a better way to do this, see readme for more info
	input_partition_rows=5,
	arguments={
		"descriptors": ["AAC", "CTDC", "CTDT"]
	}
).apply(
	"./components/filter_pdb_component",
	arguments={
		"method": "local",
		"local_pdb_path": "/data/pdb_files",
		"bucket_name": "elated-chassis-400207_dbtl_pipeline_outputs",
		"project_id": "elated-chassis-400207",
		"google_cloud_credentials_path": "/data/google_cloud_credentials.json"
	}
).apply(
	"./components/predict_protein_3D_structure_component",
).apply(
	"./components/store_pdb_component",
	arguments={
		"method": "local",
		"local_pdb_path": "/data/pdb_files/",
		"bucket_name": "elated-chassis-400207_dbtl_pipeline_outputs",
		"project_id": "elated-chassis-400207",
		"google_cloud_credentials_path": "/data/google_cloud_credentials.json"
	}
).apply(
	"./components/msa_component",
).apply(
	"./components/unikp_component",
	arguments={
		"protein_smiles_path": "/data/protein_smiles.json",
	},
).apply(
	"./components/peptide_features_component"
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