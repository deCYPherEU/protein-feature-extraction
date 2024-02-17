import pyarrow as pa
from fondant.pipeline import Pipeline
from components.lightweight_components import (
	SequenceLengthComponent,
	MolecularWeightComponent,
	AromaticityComponent,
	IsoelectricPointComponent,
	InstabilityIndexComponent
)
from components.generate_data import generate_mock_data
from components.constants import MOCK_DATA_PATH_FONDANT

# generate the mock data, also creates a parquet file
generate_mock_data()

# create a new pipeline
pipeline = Pipeline(
	name="mock_data_pipeline",
	base_path=".fondant",
	description="basic pipeline to generate a few features"
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

# apply the components
_ = dataset.apply(
	ref=SequenceLengthComponent
).apply(
	ref=MolecularWeightComponent,
).apply(
	ref=AromaticityComponent,
).apply(
	ref=IsoelectricPointComponent,
).apply(
	ref=InstabilityIndexComponent,
)


# run the pipeline using your local path to the folder, this one is mine
# fondant run local pipeline.py --extra-volumes C:\Users\denis\Desktop\stage\protein-feature-extraction\fondant-examples\data:/data