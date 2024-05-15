"""
This module calculates the hydrophobicity accessible area of a protein sequence.
"""
import freesasa

def calculate_hydrophobicity_accessible_area(pdb_file_path: str) -> float:
	"""
	Calculate the hydrophobicity of a protein structure from a PDB file.
	Uses the freesasa library to calculate the accessible surface area.
	"""

	structure = freesasa.Structure(pdb_file_path)
	result = freesasa.calc(structure)
	total_area = result.totalArea()

	# return the total area or 0.0
	return total_area if total_area else 0.0