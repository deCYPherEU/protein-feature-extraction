"""
This module calculates the buriedness of amino acid residues in the crystal structure.
"""
from typing import Dict
import logging

import numpy as np
from scipy.spatial import ConvexHull


logger = logging.getLogger(__name__)

def calculate_buriedness(structure: str) -> Dict:
	"""
	Calculate the buriedness of a protein structure from a PDB file.
	"""

	model = structure[0]

	# Initialize the buriedness object
	buriedness_object = {}

	# Remove water and hetatoms
	for res in model.get_residues():
		chain = res.parent
		if res.id[0] != " ":
			chain.detach_child(res.id)

	atoms = model.get_atoms()
	if not atoms:
		raise ValueError("Could not parse atoms in the pdb file")

	conv = ConvexHull([atom.coord for atom in atoms])
	for i, atom in enumerate(atoms):
		coord = atom.coord
		res = i + 1
		buriedness_object.setdefault(res, [])
		# Get distance from atom to closer face of `conv'
		if i in conv.vertices:
			dist = 0
			buriedness_object[res].append(dist)
		else:
			dist = np.inf
			for face in conv.equations:
				_dist = abs(np.dot(coord, face[:-1]) + face[-1])
				_dist = _dist / np.linalg.norm(face[:-1])
				if _dist < dist:
					dist = _dist
			buriedness_object[res].append(dist)

	for res in buriedness_object:
		buriedness_object[res] = np.mean(buriedness_object[res])

	return buriedness_object


def calculate_aligned_buriedness(structure: str, aligned_sequence: str) -> Dict:
	"""
	Calculate the buriedness of a protein structure from a PDB file based on an aligned sequence.
	"""
	buriedness = calculate_buriedness(structure)

	aligned_buriedness = {}
	aligned_position = 1
	buriedness_position = 1

	for _, residue in enumerate(aligned_sequence):
		if residue != "-":
			# Add the buriedness of the residue to the aligned buriedness dictionary
			aligned_buriedness[aligned_position] = buriedness.get(buriedness_position, np.nan)
			aligned_position += 1
			buriedness_position += 1
		else:
			# Add padding information to the aligned buriedness dictionary
			aligned_buriedness[aligned_position] = np.nan
			aligned_position += 1

	return str(aligned_buriedness)
