"""
The UniKP component uses the UniKP framework to predict
kinetic properties (Km, Kcat and Vmax) of a protein sequence and a ligand SMILES string.
The results will be presented as a JSON, but in a string format
for easy storage and retrieval in the dataframe.
"""
import logging
import os
import json

import pandas as pd
import requests
from requests.exceptions import RequestException
from dotenv import load_dotenv
from fondant.component import PandasTransformComponent

# Load the environment variables
load_dotenv()


logger = logging.getLogger(__name__)


class PredictEnyzmCharacteristicsComponent(PandasTransformComponent):
    """
    The UniKP component uses the UniKP framework to predict
    kinetic properties (Km, Kcat and Vmax) of a protein sequence and a ligand SMILES string.
    The results will be presented as a JSON, but in a string format
    for easy storage and retrieval in the dataframe.
    """

    def __init__(self, target_molecule_smiles: str):
        # pylint: disable=super-init-not-called

        self.caller = HfCaller()

        self.target_molecule_smiles = target_molecule_smiles

        self.check_existence_of_files()




    def check_existence_of_files(self) -> None:
        """Check if the required files exist in the local_pdb_files_path directory."""

        if not os.path.exists(self.target_molecule_smiles):
            logger.error(
                "File %s not found. Please make sure the file exists.",
                self.target_molecule_smiles)
            raise FileNotFoundError(
                f"File {self.target_molecule_smiles} not found. Please make sure the file exists.")


    def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Perform the transformation on the dataframe."""
        molecules = read_json_file(self.target_molecule_smiles)

        dataframe['unikp_kinetic_prediction'] = dataframe.apply(
            lambda x: predict_over_dataframe(
                self.caller,
                x["sequence"],
                molecules), axis=1)

        return dataframe

class HfCaller():
    """
    A class representing an API caller for predicting kinetic properties.
    Attributes:
        hf_api_key (str): The API key for accessing the API.
        hf_endpoint_url (str): The endpoint URL for making API calls.
    Methods:
        __init__(): Initializes the HfCaller object.
        get_headers(): Returns the headers for the API call.
        predict_kinetic_properties(protein_sequence, target_smile): Predicts kinetic properties
        using the API.
    """
    def __init__(self) -> None:
        """
        Initializes the class instance.
        Raises:
            ValueError: If the environment variables `HF_API_KEY` or `HF_ENDPOINT_URL` are not set.
        """
        self.hf_api_key = os.getenv("HF_API_KEY")
        self.hf_endpoint_url = os.getenv("HF_ENDPOINT_URL")

        if not self.hf_api_key or not self.hf_endpoint_url:
            raise ValueError("environment variables not set.")

    def get_headers(self):
        """Get headers for the API call."""
        return {
            "Authorization": f"Bearer {self.hf_api_key}",
            "Content-Type": "application/json"
        }

    def predict_kinetic_properties(
        self,
        protein_sequence: str,
        target_smile: str) -> dict:
        """
        Predicts kinetic properties for a given protein sequence and target SMILES.

        Args:
            protein_sequence (str): The protein sequence.
            target_smile (str): The target SMILES.

        Returns:
            dict: A dictionary containing the predicted kinetic properties.

        Raises:
            RequestException: If the request to the endpoint fails.
        """

        data = {
                    "inputs": {
                        "sequence": protein_sequence,
                        "smiles": target_smile
                    }
                }
        try:
            response = requests.post(
                self.hf_endpoint_url, json=data, headers=self.get_headers(), timeout=30)
            response.raise_for_status()
        except RequestException as e:
            logger.error("Request failed: %s", e)
            return None

        return response.json()

def read_json_file(path):
    """
    Reads a JSON file and returns its contents as a Python dictionary.
    Args:
        path (str): The path to the JSON file.
    Returns:
        dict: The contents of the JSON file as a Python dictionary.
    """
    with open(path, "r") as f:
        data = json.load(f)
    return data

def predict_over_dataframe(huggingface, sequence, f):
    """
    Predicts kinetic properties over a dataframe of SMILES strings.
    Args:
        huggingface (object): The HuggingFace model used for prediction.
        sequence (str): The sequence used for prediction.
        f (dict): A dictionary containing the names and SMILES strings.
    Returns:
        dict: A dictionary containing the predicted results for each name.
    """
    out = {}
    for name, smiles in f.items():
        print(name, smiles)
        result = huggingface.predict_kinetic_properties(sequence, smiles)
        out[name] = result
    return out
