"""
This module calculates the hydrophobicity of a protein sequence.
"""
from Bio.PDB import PDBParser
from Bio.SeqUtils.ProtParamData import kd


def calculate_hydrophobicity(pdb_file_path: str) -> float:
	"""
	Calculate the hydrophobicity of a protein structure from a PDB file.
	"""

	parser = PDBParser()
	structure = parser.get_structure("protein", pdb_file_path)

	hydrophobicity = {}

	for model in structure:
		for chain in model:
			for residue in chain:
				residue_id = residue.get_id()[1]
				residue_aa = residue.get_resname()[0]
				hydrophobicity[residue_id] = kd.get(residue_aa, 0.0)

				for other_residue in chain:
					if residue != other_residue:
						other_residue_aa = other_residue.get_resname()[0]

						try:
							distance = residue['CA'] - other_residue['CA']
						except KeyError:
							continue

						if distance < 8:
							hydrophobicity[residue_id] += kd.get(
								other_residue_aa, 0.0)

	# get the average hydrophobicity
	average_hydrophobicity = sum(
		hydrophobicity.values()) / len(hydrophobicity)

	return average_hydrophobicity
