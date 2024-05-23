# UniKP component

The UniKP component is used to predict the kinetic parameters of a protein sequence and substrate (SMILES) pair. The component uses the [UniKP model](https://github.com/Luo-SynBioLab/UniKP) to predict the kinetic parameters.

This component will use each protein sequence and substrate pair provided in the `json` file provided in the `protein_smiles_path` of the `arguments` of the component.

This file should look like this:

```json
{
	"MTEYKLVVVGAGGVGKSAL...": ["CC(=O)O", "CC(=O)OC1=CC=CC=C1C(=O)O", ...],
	...
}
```

This file should contain all the protein sequences of the input dataframe and at least one substrate SMILES for each protein sequence.

The requests will be sent using `Hugging Face` where the model is hosted. The response will be a `json` file with the following structure:

```json
{
  "CC(=O)Nc1ccc(O)cc1": {"Km": 0.123, "Kcat": 0.123, "Vmax": 0.123},
  "CC[C...": {"Km": 0.123, "Kcat": 0.123, "Vmax": 0.123}
}
```

A request will be sent for each protein sequence and substrate pair. The response will contain the kinetic parameters for a single pair, the code will concatenate all the responses into a single column.

## Env Setup

The following arguments will need to be provided for this component in the `pipeline.py` file:

```yaml
	protein_smiles_path:
		type: str
		description: "The path to the json file containing the protein sequences and substrate SMILES."
		default: None
```

Make sure you have the `protein_smiles.json` file in the `data` folder. This file is needed to provide the protein sequences and substrate SMILES pairs.

You'll also need to add a `.env` file in the component folder with the following environment variables:

```yaml
HF_API_KEY=""
HF_ENDPOINT_URL=""
```
