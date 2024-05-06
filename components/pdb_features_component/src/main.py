"""
The PDBFeaturesComponent takes as argument the pdb file
as string and will calculate features such as contact order, LRO, etc.
"""
import logging
from itertools import combinations
from typing import Tuple
import pandas as pd
import numpy as np
from scipy.spatial import ConvexHull
from Bio.PDB.Polypeptide import index_to_one, three_to_index
from Bio.PDB import PDBParser
from Bio.SeqUtils.ProtParamData import kd
import freesasa
from fondant.component import PandasTransformComponent

# Set up logging
logger = logging.getLogger(__name__)


class PDBFeaturesComponent(PandasTransformComponent):
	"""
	The PDBFeaturesComponent takes as argument the pdb file
	as string and will calculate features such as contact order, LRO, etc.
	"""

	def __init__(self, *_):
		self.pdb_file = "temp.pdb"

	def transform(self, dataframe: pd.DataFrame) -> pd.DataFrame:
		"""
		Transforms the input dataframe by calculating the features of the PDB file.
		"""

		"""
		dataframe["pdb_contact_order"] = dataframe["pdb_string"].apply(
			lambda pdb_string: self.calculate_contact_order(pdb_string, atom_type='CA', cutoff=8))

		dataframe["pdb_lro"] = dataframe["pdb_string"].apply(
			lambda pdb_string: self.calculate_long_range_order(pdb_string))

		dataframe["pdb_contacts_8A_ca"] = dataframe["pdb_string"].apply(
			lambda pdb_string: self.calculate_number_of_contacts(pdb_string, cutoff=8, atom_type='CA'))

		dataframe["pdb_contacts_14A_ca"] = dataframe["pdb_string"].apply(
			lambda pdb_string: self.calculate_number_of_contacts(pdb_string, cutoff=14, atom_type='CA'))
		
		"""
		dataframe["pdb_aligned_buriedness"] = dataframe.apply(
			lambda row: self.calculate_aligned_buriedness(row["pdb_string"], row["msa_sequence"]), axis=1)
		"""

		dataframe["pdb_aa_distances_matrix"] = dataframe.apply(
			lambda row: self.calculate_buriedness(row["pdb_string"], row["msa_sequence"]), axis=1)

		dataframe["pdb_avg_short_range"] = dataframe["pdb_string"].apply(
			lambda pdb_string: self.calculate_interactions(pdb_string)[0])

		dataframe["pdb_avg_medium_range"] = dataframe["pdb_string"].apply(
			lambda pdb_string: self.calculate_interactions(pdb_string)[1])

		dataframe["pdb_avg_long_range"] = dataframe["pdb_string"].apply(
			lambda pdb_string: self.calculate_interactions(pdb_string)[2])
		
		dataframe["pdb_avg_hydrophobicity"] = dataframe["pdb_string"].apply(
			lambda pdb_string: self.calculate_hydrophobicity(pdb_string))
		
		dataframe["pdb_hydrophobicity_accessible_area"] = dataframe["pdb_string"].apply(
			lambda pdb_string: self.calculate_hydrophobicity_accessible_area(pdb_string))
		"""

		return dataframe

	def write_pdb_to_file(self, pdb_string: str, filename: str) -> None:
		"""
		Write a PDB string to a file.
		"""

		with open(filename, "w") as f:
			f.write(pdb_string)

	def calculate_contact_order(self, pdb_string: str, atom_type='CA', cutoff=8) -> float:
		"""
		Calculate the number of contacts between amino acid residues in the crystal structure.
		"""

		# write pdb string to a file
		self.write_pdb_to_file(pdb_string, self.pdb_file)

		parser = PDBParser()
		structure = parser.get_structure("protein", self.pdb_file)

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

	def calculate_long_range_order(self, pdb_string: str) -> float:
		"""
		Calculate the Long Range Order (LRO) of a protein structure from a PDB file.
		"""

		# write pdb string to a file
		self.write_pdb_to_file(pdb_string, self.pdb_file)

		parser = PDBParser()
		structure = parser.get_structure("protein", self.pdb_file)

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

	def calculate_number_of_contacts(self, pdb_string: str, cutoff: int, atom_type='CA') -> int:
		"""
		Calculate the number of contacts between amino acid residues in the crystal structure.
		"""

		# write pdb string to a file
		self.write_pdb_to_file(pdb_string, self.pdb_file)

		parser = PDBParser()
		structure = parser.get_structure("protein", self.pdb_file)

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

	def calculate_buriedness(self, pdb_string: str) -> float:
		"""
		Calculate the buriedness of a protein structure from a PDB file.
		https://github.com/rodogi/buriedness/blob/master/buriedness.py
		"""

		# write pdb string to a file
		self.write_pdb_to_file(pdb_string, self.pdb_file)

		parser = PDBParser()
		structure = parser.get_structure("protein", self.pdb_file)
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

	def calculate_aligned_buriedness(self, pdb_string: str, aligned_sequence: str) -> dict:
		"""
		Calculate the buriedness of a protein structure from a PDB file based on an aligned sequence.
		"""
		buriedness = self.calculate_buriedness(pdb_string)

		aligned_buriedness = {}
		aligned_position = 1
		buriedness_position = 1
		for i, residue in enumerate(aligned_sequence):
			if residue == "-":
				# add the buriedness of 'nan' for gaps and keep track of this position in the aligned sequence
				aligned_buriedness[f"PAD-{aligned_position}"] = np.nan
				aligned_position += 1
			else:
				# add the buriedness of the residue and keep track of this position in the aligned sequence
				aligned_buriedness[f"{residue}-{aligned_position}"] = buriedness[f"{residue}-{buriedness_position}"]
				aligned_position += 1
				buriedness_position += 1

		return str(aligned_buriedness)

	def calculate_distances(self, pdb_string: str, aligned_sequence: str) -> Tuple[str, str, str]:
		"""
		Calculate the sparse matrix of distances between amino acids in a protein structure from a PDB file.
		"""

		# write pdb string to a file
		self.write_pdb_to_file(pdb_string, self.pdb_file)

		parser = PDBParser()
		structure = parser.get_structure("protein", self.pdb_file)
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

	def calculate_interactions(self, pdb_string: str) -> Tuple[str, str, str]:
		"""
		Calculate the interactions between amino acids in a protein structure from a PDB file.

		Returns the average short range, medium range and long range interactions.
		"""

		# write pdb string to a file
		self.write_pdb_to_file(pdb_string, self.pdb_file)

		parser = PDBParser()
		structure = parser.get_structure("protein", self.pdb_file)

		# Get the model and chain
		model = structure[0]
		chain = model['A']  # Assuming chain A

		# Initialize total distances
		total_short_range = 0
		total_medium_range = 0
		total_long_range = 0

		# Loop over each residue in the chain
		for target_residue in chain:
			# Calculate interactions for the current residue
			for residue in chain:
				if residue != target_residue:
					try:
						distance = target_residue["CA"] - residue["CA"]
					except KeyError:
						continue

					if distance <= 2:
						total_short_range += distance
					elif 3 <= distance <= 4:
						total_medium_range += distance
					else:
						total_long_range += distance

		average_short_range = total_short_range/len(list(chain.get_residues()))
		average_medium_range = total_medium_range / \
			len(list(chain.get_residues()))
		average_long_range = total_long_range/len(list(chain.get_residues()))

		return average_short_range, average_medium_range, average_long_range

	def calculate_hydrophobicity(self, pdb_string: str) -> float:
		"""
		Calculate the hydrophobicity of a protein structure from a PDB file.
		"""

		# write pdb string to a file
		self.write_pdb_to_file(pdb_string, self.pdb_file)

		parser = PDBParser()
		structure = parser.get_structure("protein", self.pdb_file)

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

	def calculate_hydrophobicity_accessible_area(self, pdb_string: str) -> float:
		"""
		Calculate the hydrophobicity of a protein structure from a PDB file.
		Uses the freesasa library to calculate the accessible surface area.
		"""

		# write pdb string to a file
		self.write_pdb_to_file(pdb_string, self.pdb_file)

		structure = freesasa.Structure(self.pdb_file)
		result = freesasa.calc(structure)
		total_area = result.totalArea()

		# return the total area or 0.0
		return total_area if total_area else 0.0
