# PDB Features Component

The PDB Features Component is a component that provides a set of features for a given PDB file. This file should be present in a string format in the column `pdb_string` of the input dataframe.

The most interesting features are chosen by Pieter Coussement and are taken from the following paper: [PDBparam](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4909059/).

## Env Setup

No environment variables are needed for this component.

The input dataframe should contain the `pdb_string` column, which is obtainable by using the [filter_pdb_component](../filter_pdb_component/README.md), [predict_protein_3D_structure_component](../predict_protein_3D_structure_component/README.md) and [store_pdb_component](../store_pdb_component/README.md). These components do require environments variables to be set.
