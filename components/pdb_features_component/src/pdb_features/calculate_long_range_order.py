"""
This module calculates the long-range order of a protein structure.
"""
import numpy as np
from Bio.PDB import PDBParser

def calculate_long_range_order(pdb_file_path: str) -> float:
	"""
	Calculate the Long Range Order (LRO) of a protein structure from a PDB file.
	"""

	parser = PDBParser()
	structure = parser.get_structure("protein", pdb_file_path)


	distances = []
	# use only the first model in the structure
	model = structure[0]
	for chain in model:
		residues = list(chain.get_residues())

		# keep only the residues with CA atoms
		residues = [residue for residue in residues if "CA" in residue]

		for i, residue1 in enumerate(residues):
			for j, residue2 in enumerate(residues):
				if i < j:
					ca1 = residue1["CA"].coord
					ca2 = residue2["CA"].coord
					distance = np.linalg.norm(ca1 - ca2)
					distances.append(distance)

	if len(distances) == 0:
		return 0.0
	else:
		return np.mean(distances)
