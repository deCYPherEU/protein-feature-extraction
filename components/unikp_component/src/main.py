"""
The UniKP component uses the UniKP framework to predict
kinetic properties (Km, Kcat and Vmax) of a protein sequence and a ligand SMILES string.
The results will be presented as a JSON, but in a string format
for easy storage and retrieval in the dataframe.
"""
import logging
import os
import requests
import json
from dotenv import load_dotenv
import pandas as pd
from fondant.component import PandasTransformComponent

# Load the environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)


class PredictProtein3DStructureComponent(PandasTransformComponent):
    """
    The UniKP component uses the UniKP framework to predict
    kinetic properties (Km, Kcat and Vmax) of a protein sequence and a ligand SMILES string.
    The results will be presented as a JSON, but in a string format
    for easy storage and retrieval in the dataframe.
    """

    def __init__(self, protein_smiles_path: str):
        self.hf_api_key = os.getenv("HF_API_KEY")
        self.hf_endpoint_url = os.getenv("HF_ENDPOINT_URL")
        self.empty_prediction = {
            "Km": None,
            "Kcat": None,
            "Vmax": None
        }

        self.protein_smiles_path = protein_smiles_path

        if not self.hf_api_key or not self.hf_endpoint_url:
            raise Exception("environment variables not set.")

    def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Perform the transformation on the dataframe."""

        # load the json file
        with open(self.protein_smiles_path, "r") as f:
            data = json.load(f)

        for protein_sequence, smiles_list in data.items():
            predictions = {}
            for smiles in smiles_list:
                result = self.predict_kinetic_properties(
                    protein_sequence, smiles)
                if result is not None:
                    predictions[smiles] = result
                else:
                    predictions[smiles] = self.empty_prediction

            dataframe.loc[dataframe["sequence"] == protein_sequence, [
                "unikp_kinetic_prediction"]] = str(json.dumps(predictions))

        return dataframe

    def predict_kinetic_properties(self, protein_sequence: str, ligand_smiles: str) -> str:
        """
        Predict the kinetic properties of a protein sequence and a ligand SMILES string.
        """
        # Prepare the data
        data = {
            "inputs": {
                "sequence": protein_sequence,
                "smiles": ligand_smiles
            }
        }

        # Make the API call
        headers = {
            "Authorization": f"Bearer {self.hf_api_key}",
            "Content-Type": "application/json"
        }
        response = requests.post(self.hf_endpoint_url,
                                 json=data, headers=headers)

        # Check if the request was successful
        if response.status_code != 200:
            raise Exception(
                f"Request failed with status code {response.status_code} and response {response.text}")

        # Return the pdb string
        return response.json()
