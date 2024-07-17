def convert_aa_outcome_to_msa(outcome, MSA):
    pass



def remove_water(structure):
    """
    Remove water and hetatoms from a structure.
    """
    model = structure[0]

    for res in model.get_residues():
        chain = res.parent
        if res.id[0] != " ":
            chain.detach_child(res.id)

    return model
