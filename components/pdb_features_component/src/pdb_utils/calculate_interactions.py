"""
This module calculates the interactions between amino acid residues in the crystal structure.
"""
from typing import Tuple


def calculate_interactions(structure: str) -> Tuple[str, str, str]:
    """
    Calculate the interactions between amino acids in a protein structure from a PDB file.

    Returns the average short range, medium range and long range interactions.
    """

    # Get the model and chain
    model = structure[0]
    chain = model['A']

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
