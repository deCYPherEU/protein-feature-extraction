"""
This module calculates the number of contacts between amino acid residues in the crystal structure.
"""

import numpy as np
from Bio.PDB import PDBParser

def calculate_number_of_contacts(structure: str, cutoff: float, atom_type: str) -> int:
	"""
	Calculate the number of contacts between amino acid residues in the crystal structure.
	"""

	contacts = 0
	# use only the first model in the structure
	model = structure[0]
	for chain in model:
		residues = list(chain.get_residues())

		# keep only the residues with the specified atom type
		residues = [
			residue for residue in residues if atom_type in residue]

		for i, residue1 in enumerate(residues):
			for j, residue2 in enumerate(residues):
				if i < j:
					atom1 = residue1[atom_type].coord
					atom2 = residue2[atom_type].coord
					distance = np.linalg.norm(atom1 - atom2)
					if distance <= cutoff:
						contacts += 1

	return contacts