"""
The PDBFeaturesComponent takes as argument the pdb file
as string and will calculate features such as contact order, LRO, etc.
"""
import logging

import pandas as pd
from fondant.component import PandasTransformComponent
from Bio.PDB import PDBParser

from pdb_utils.calculate_buriedness import calculate_aligned_buriedness
from pdb_utils.calculate_distance_matrix import calculate_distance_matrix
from pdb_utils.calculate_hydrophobicity import calculate_hydrophobicity
from pdb_utils.calculate_hydrophobicity_accessible_area import calculate_hydrophobicity_accessible_area
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
		pass

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""
		Transforms the input dataframe by calculating the features of the PDB file.
		"""

		for idx, row in dataframe.iterrows():
			pdb_file_path = f"temp_{idx}.pdb"
			self.write_pdb_to_file(row["pdb_string"], pdb_file_path)

			# Create the structure here
			parser = PDBParser()
			structure = parser.get_structure("protein", pdb_file_path)

			# Perform calculations using the saved PDB file
			dataframe.at[idx, "pdb_lro"] = calculate_long_range_order(
				structure)
			dataframe.at[idx, "pdb_contacts_8A_ca"] = calculate_number_of_contacts(
				structure, cutoff=8, atom_type='CA')
			dataframe.at[idx, "pdb_contacts_14A_ca"] = calculate_number_of_contacts(
				structure, cutoff=14, atom_type='CA')
			dataframe.at[idx, "pdb_buriedness"] = calculate_aligned_buriedness(
				structure, row["msa_sequence"])
			dataframe.at[idx, "pdb_aa_distances_matrix"] = calculate_distance_matrix(
				structure, row["msa_sequence"])

			interactions = calculate_interactions(structure)
			dataframe.at[idx, "pdb_avg_short_range"] = interactions[0]
			dataframe.at[idx, "pdb_avg_medium_range"] = interactions[1]
			dataframe.at[idx, "pdb_avg_long_range"] = interactions[2]

			dataframe.at[idx, "pdb_avg_hydrophobicity"] = calculate_hydrophobicity(
				structure)
			dataframe.at[idx, "pdb_hydrophobicity_accessible_area"] = calculate_hydrophobicity_accessible_area(
				pdb_file_path)

		return dataframe

	def write_pdb_to_file(self, pdb_string: str, filename: str) -> None:
		"""
		Write a PDB string to a file.
		"""
		with open(filename, "w", encoding="utf-8") as f:
			f.write(pdb_string)
