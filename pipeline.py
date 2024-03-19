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
    "Subcellular location [CC]": "subcellular_location",
}

# read the dataset
dataset = pipeline.read(
	"load_from_parquet",
	arguments={
		"dataset_uri": "/data",
        "column_name_mapping": load_component_column_mapping,
	},
    produces={
        "entry_name": pa.string(), 
        "entry": pa.string(), 
        "gene_name": pa.string(), 
        "length": pa.int32(), 
        "sequence": pa.string(), 
        "subcellular_location": pa.string()
    }
)

dataset = dataset.apply(
    "./components/biopython_component"
)

# dataset.write(
# 	"write_to_file",
# 	arguments={
# 		"path": "/data/output",
# 	}
# )

# run the pipeline
runner = DockerRunner()
runner.run(
    input=pipeline,
    extra_volumes=["/Users/sharongrundmann/Projects/client-work/decypher/protein-feature-extraction/data:/data"]
)
