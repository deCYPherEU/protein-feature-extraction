from Bio.PDB import Structure, Model, Chain, Residue, Atom, PDBIO

# Define a dictionary mapping amino acids to their side-chain atoms
side_chain_atoms = {
    'A': ['CB'],
    'C': ['CB', 'SG'],
    'D': ['CB', 'CG', 'OD1', 'OD2'],
    'E': ['CB', 'CG', 'CD', 'OE1', 'OE2'],
    'F': ['CB', 'CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ'],
    'G': [],
    'H': ['CB', 'CG', 'ND1', 'CD2', 'CE1', 'NE2'],
    'I': ['CB', 'CG1', 'CG2', 'CD1'],
    'K': ['CB', 'CG', 'CD', 'CE', 'NZ'],
    'L': ['CB', 'CG', 'CD1', 'CD2'],
    'M': ['CB', 'CG', 'SD', 'CE'],
    'N': ['CB', 'CG', 'OD1', 'ND2'],
    'P': ['CB', 'CG', 'CD'],
    'Q': ['CB', 'CG', 'CD', 'OE1', 'NE2'],
    'R': ['CB', 'CG', 'CD', 'NE', 'CZ', 'NH1', 'NH2'],
    'S': ['CB', 'OG'],
    'T': ['CB', 'OG1', 'CG2'],
    'V': ['CB', 'CG1', 'CG2'],
    'W': ['CB', 'CG', 'CD1', 'CD2', 'NE1', 'CE2', 'CE3', 'CZ2', 'CZ3', 'CH2'],
    'Y': ['CB', 'CG', 'CD1', 'CD2', 'CE1', 'CE2', 'CZ', 'OH']
}

def create_pdb(protein_sequence, protein_name):
    structure = Structure.Structure("protein_structure")
    model = Model.Model(0)
    structure.add(model)
    chain = Chain.Chain("A")
    model.add(chain)

    for i, aa in enumerate(protein_sequence):
        # Create a new residue
        residue = Residue.Residue((' ', i + 1, ' '), aa, i + 1)
        chain.add(residue)
        
        # Add backbone atoms
        residue.add(Atom.Atom("N", (i + 1, 0, 0), 1, 1, " ", "N", i + 1, "N"))
        residue.add(Atom.Atom("CA", (i + 1, 0, 0), 1, 1, " ", "CA", i + 1, "C"))
        residue.add(Atom.Atom("C", (i + 1, 0, 0), 1, 1, " ", "C", i + 1, "C"))
        residue.add(Atom.Atom("O", (i + 1, 0, 0), 1, 1, " ", "O", i + 1, "O"))

        # Add side-chain atoms
        for atom_name in side_chain_atoms.get(aa, []):
            residue.add(Atom.Atom(atom_name, (i + 1, 0, 0), 1, 1, " ", atom_name, i + 1, "C"))

    io = PDBIO()
    io.set_structure(structure)
    io.save(f"./pdb_files/{protein_name}.pdb")
