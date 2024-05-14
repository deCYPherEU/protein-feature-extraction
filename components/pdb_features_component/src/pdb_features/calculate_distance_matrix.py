"""
This module calculates the distance matrix of a protein structure.
"""
from typing import Tuple
from Bio.PDB import PDBParser
import numpy as np
from itertools import combinations

def calculate_distance_matrix(pdb_file_path: str, aligned_sequence: str) -> Tuple[str, str, str]:
	"""
	Calculate the sparse matrix of distances between amino acids in a
	protein structure from a PDB file.
	"""

	parser = PDBParser()
	structure = parser.get_structure("protein", pdb_file_path)
	max_length = len(aligned_sequence)

	# Initialize a sparse matrix to store distances
	sparse_matrix = np.zeros((max_length, max_length))

	# Iterate over all chains in the structure
	for chain in structure.get_chains():
		# Iterate over all residues in the chain
		for res1, res2 in combinations(chain.get_residues(), 2):
			# Calculate the distance between the alpha carbons of the residues
			try:
				# Find corresponding positions in aligned sequence
				pos1 = res1.get_id()[1] - 1
				pos2 = res2.get_id()[1] - 1

				# Calculate the distance only if both positions are within aligned sequence length
				if pos1 < max_length and pos2 < max_length:
					distance = np.linalg.norm(
						res1['CA'].get_coord() - res2['CA'].get_coord())
					sparse_matrix[pos1, pos2] = distance
					sparse_matrix[pos2, pos1] = distance
			except KeyError:
				pass

	return sparse_matrix
