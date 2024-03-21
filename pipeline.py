import logging
import pyarrow as pa

from fondant.pipeline import Pipeline
from fondant.pipeline.runner import DockerRunner


logger = logging.getLogger(__name__)


# create a new pipeline
pipeline = Pipeline(
	name="feature_extraction_pipeline",
	base_path=".fondant",
	description="A pipeline to extract features from protein sequences."
)

load_component_column_mapping = {
    "Entry Name": "entry_name",
    "Entry": "entry",
    "Gene Names": "gene_name",
    "Length": "length",
    "Sequence": "sequence",
    "Subcellular location [CC]": "subcellular_location_[cc]",
}

# read the dataset
dataset = pipeline.read(
	"load_from_parquet",
	arguments={
		"dataset_uri": "/data",
        "column_name_mapping": load_component_column_mapping,
	},
    produces={
        "sequence": pa.string(),
    }
)

dataset = dataset.apply(
    "./components/biopython_component"
)

dataset.write(
    "write_to_file",
	arguments={
		"path": "/data/output",
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
        "charge_at_pH_5": pa.float64(),
        "charge_at_pH_7": pa.float64(),
        # "molar_extinction_coefficient_oxidized": pa.int64(),
        # "molar_extinction_coefficient_reduced": pa.int64(),
    }
)

# run the pipeline
runner = DockerRunner()
runner.run(
    input=pipeline,
    extra_volumes=["/Users/sharongrundmann/Projects/client-work/decypher/protein-feature-extraction/data:/data"]
)
