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
from Bio.PDB import PDBParser
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

		dataframe["pdb_contact_order"] = dataframe["pdb_string"].apply(
			lambda pdb_string: self.calculate_contact_order(pdb_string, atom_type='CA', cutoff=8))

		dataframe["pdb_lro"] = dataframe["pdb_string"].apply(
			lambda pdb_string: self.calculate_long_range_order(pdb_string))

		dataframe["pdb_contacts_8A_ca"] = dataframe["pdb_string"].apply(
			lambda pdb_string: self.calculate_number_of_contacts(pdb_string, cutoff=8, atom_type='CA'))

		dataframe["pdb_contacts_14A_ca"] = dataframe["pdb_string"].apply(
			lambda pdb_string: self.calculate_number_of_contacts(pdb_string, cutoff=14, atom_type='CA'))

		dataframe["pdb_buriedness"] = dataframe["pdb_string"].apply(
			lambda pdb_string: self.calculate_buriedness(pdb_string))

		dataframe["pdb_short_distances"] = dataframe["pdb_string"].apply(
			lambda pdb_string: self.calculate_distances(pdb_string)[0])

		dataframe["pdb_medium_distances"] = dataframe["pdb_string"].apply(
			lambda pdb_string: self.calculate_distances(pdb_string)[1])

		dataframe["pdb_long_distances"] = dataframe["pdb_string"].apply(
			lambda pdb_string: self.calculate_distances(pdb_string)[2])

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

		https://github.com/rodogi/buriedness/blob/master/buriedness.py
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

	def calculate_buriedness(self, pdb_string: str) -> str:
		"""
		Calculate the buriedness of a protein structure from a PDB file.
		"""

		bdness_object = {}
		# write pdb string to a file
		self.write_pdb_to_file(pdb_string, self.pdb_file)

		parser = PDBParser()
		structure = parser.get_structure("protein", self.pdb_file)
		model = structure[0]

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
			res = (atom.parent.parent.id
				+ atom.parent.resname + str(atom.parent.id[1]))
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

		return str(bdness_object)

	def calculate_distances(self, pdb_string: str) -> Tuple[str, str, str]:
		"""
		Calculate short (< 8), medium (< 12 and >= 8) and long (> 12) distances
		between all amino acids in a protein structure from a PDB file.
		"""

		# write pdb string to a file
		self.write_pdb_to_file(pdb_string, self.pdb_file)

		parser = PDBParser()
		structure = parser.get_structure("protein", self.pdb_file)

		# Initialize a dictionary to store distances
		short_distances = {}
		medium_distances = {}
		long_distances = {}

		for chain in structure.get_chains():
			for res1, res2 in combinations(chain.get_residues(), 2):
				try:
					distance = np.linalg.norm(
						res1['CA'].get_coord() - res2['CA'].get_coord())
					if distance < 8:
						short_distances[(res1.get_id()[1],
										res2.get_id()[1])] = distance
					if distance < 12 and distance >= 8:

						medium_distances[(res1.get_id()[1],
										res2.get_id()[1])] = distance
					if distance >= 12:
						long_distances[(res1.get_id()[1],
										res2.get_id()[1])] = distance
				except KeyError:
					pass

		return str(short_distances), str(medium_distances), str(long_distances)
