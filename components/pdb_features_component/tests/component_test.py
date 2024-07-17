import tempfile
from pathlib import Path
import os
import pandas as pd
import pyarrow as pa
import pytest

from src.main import PDBFeaturesComponent

@pytest.fixture
def load_external_file():
    # Adjust the path to your external file
    file_path = 'tests/data/data.json'
    data = pd.read_json(file_path)
    return data





def test_pdb_component(load_external_file):
    dataframe = load_external_file
    # load code from component
    component = PDBFeaturesComponent()

    f = component.transform(dataframe)

    
    f.drop('pdb_string', axis=1).to_csv("test.csv", index=False)




