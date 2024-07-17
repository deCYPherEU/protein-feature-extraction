"""
The PDBFeaturesComponent takes as argument the pdb file
as string and will calculate features such as contact order, LRO, etc.
"""
import logging

import pandas as pd
from Bio.PDB import PDBParser

import tempfile

from fondant.component import PandasTransformComponent

from pdb_utils.calculate_buriedness import calculate_aligned_buriedness
from pdb_utils.calculate_distance_matrix import calculate_distance_matrix
from pdb_utils.calculate_hydrophobicity import calculate_hydrophobicity
from pdb_utils.calculate_hydrophobicity_accessible_area import \
    calculate_hydrophobicity_accessible_area
from pdb_utils.calculate_interactions import calculate_interactions
from pdb_utils.calculate_long_range_order import calculate_long_range_order
from pdb_utils.calculate_number_of_contacts import calculate_number_of_contacts


logger = logging.getLogger(__name__)


class PDBFeaturesComponent(PandasTransformComponent):
    """
    The PDBFeaturesComponent takes as argument the pdb file
    as string and will calculate features such as contact order, LRO, etc.
    """

    def __init__(self, *_):
        # pylint: disable=super-init-not-called
        pass

    def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Transforms the input dataframe by calculating the features of the PDB file.
        """
        parser = PDBParser()
        for idx, row in dataframe.iterrows():
            with tempfile.NamedTemporaryFile(delete=False) as fp:
                fp.write(row["pdb_string"].encode())
                fp.close()

                structure = parser.get_structure("protein", fp.name)

                dataframe.at[idx, "pdb_lro"] = calculate_long_range_order(
                    structure)

                dataframe.at[idx, "pdb_contacts_8A_ca"] = calculate_number_of_contacts(
                    structure, cutoff=8, atom_type='CA')
                dataframe.at[idx, "pdb_contacts_14A_ca"] = calculate_number_of_contacts(
                    structure, cutoff=14, atom_type='CA')
                dataframe.at[idx, "pdb_buriedness"] = calculate_aligned_buriedness(
                    structure, row["msa_sequence"])
                # dataframe.at[idx, "pdb_aa_distances_matrix"] = calculate_distance_matrix(
                #     structure, row["msa_sequence"])

            # interactions = calculate_interactions(structure)
            # dataframe.at[idx, "pdb_avg_short_range"] = interactions[0]
            # dataframe.at[idx, "pdb_avg_medium_range"] = interactions[1]
            # dataframe.at[idx, "pdb_avg_long_range"] = interactions[2]

            # dataframe.at[idx, "pdb_avg_hydrophobicity"] = calculate_hydrophobicity(
            #     structure)
            # dataframe.at[idx, "pdb_hydrophobicity_accessible_area"] = \
            #     calculate_hydrophobicity_accessible_area(pdb_file_path)
        return dataframe

