"""
This module calculates the buriedness of amino acid residues in the crystal structure.
"""
import numpy as np
from Bio.PDB import PDBParser
from scipy.spatial import ConvexHull
from Bio.PDB.Polypeptide import index_to_one, three_to_index

import logging

logger = logging.getLogger(__name__)

def calculate_buriedness(pdb_file_path: str) -> float:
	"""
	Calculate the buriedness of a protein structure from a PDB file.
	https://github.com/rodogi/buriedness/blob/master/buriedness.py
	"""

	parser = PDBParser()
	structure = parser.get_structure("protein", pdb_file_path)
	model = structure[0]

	# Initialize the buriedness object
	bdness_object = {}

	# Remove water and hetatoms
	for res in model.get_residues():
		chain = res.parent
		if res.id[0] != " ":
			chain.detach_child(res.id)

	atoms = [atom for atom in model.get_atoms()]
	if not atoms:
		raise Exception("Could not parse atoms in the pdb file")

	conv = ConvexHull([atom.coord for atom in atoms])
	for i, atom in enumerate(atoms):
		coord = atom.coord
		res = f"{index_to_one(three_to_index(atom.parent.resname))}-{str(atom.parent.id[1])}"
		bdness_object.setdefault(res, [])
		# Get distance from atom to closer face of `conv'
		if i in conv.vertices:
			dist = 0
			bdness_object[res].append(dist)
		else:
			dist = np.inf
			for face in conv.equations:
				_dist = abs(np.dot(coord, face[:-1]) + face[-1])
				_dist = _dist / np.linalg.norm(face[:-1])
				if _dist < dist:
					dist = _dist
			bdness_object[res].append(dist)

	for res in bdness_object:
		bdness_object[res] = np.mean(bdness_object[res])

	return bdness_object


def calculate_aligned_buriedness(pdb_file_path: str, aligned_sequence: str) -> dict:
	"""
	Calculate the buriedness of a protein structure from a PDB file based on an aligned sequence.
	"""
	buriedness = calculate_buriedness(pdb_file_path)
	aligned_buriedness = {}
	aligned_position = 1
	buriedness_position = 1
	for i, residue in enumerate(aligned_sequence):
		if residue == "-":
			# add the buriedness of 'nan' for gaps in the aligned sequence
			aligned_buriedness[f"PAD-{aligned_position}"] = np.nan
			aligned_position += 1
		else:
			# add the buriedness of the residue in the aligned sequence
			logger.info(f"{residue}-{aligned_position}")
			logger.info(f"{residue}-{buriedness_position}")
			aligned_buriedness[f"{residue}-{aligned_position}"] = \
				buriedness[f"{residue}-{buriedness_position}"]
			aligned_position += 1
			buriedness_position += 1

	return str(aligned_buriedness)
