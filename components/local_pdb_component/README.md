# Local PDB Component

The Local PDB component is a custom component that is used to generate the tertiary structure of a protein sequence using the ESMFold model. The Local PDB component makes use a local folder to store the pdb files.

## Environment Variables

The following environment variables are used in the Local PDB component:

```py
HF_API_KEY="YOUR_API_KEY"
HF_ENDPOINT_URL="YOUR_ENDPOINT_URL"
```

The arguments for this Fondant component requires you to add a local folder, which is present in the `data` directory. This may or may not already contain pdb files (using the right checksum). This folder is accessed via the `--extra-volumes` argument.

The `config.py` file will direct Fondant to the right location of the files. If you place the file in a different location, you will need to change the `config.py` file accordingly. You may change the folder name, but make sure to change the `config.py` file as well.

The default folder name is `/data/pdb_files`.

## Executing the Pipeline

If there are any pdb files present in the `pdb_files` folder, make sure to use the right checksum operation for your filename. The following code shows you how to use the checksum operation using the sequence column of the dataset. The `crc64` operator is used from the `Bio.SeqUtils.CheckSum` module from the Biopython library:

```python
import Bio.SeqUtils.CheckSum.crc64
import pandas as pd

dataframe["sequence_id"] = dataframe["sequence"].apply(lambda x: Bio.SeqUtils.CheckSum.crc64(x))
```

If you want to execute the pipeline using local pdb files, you need to run the following command:

```bash
PS> fondant run local pipeline.py --extra-volumes YOUR\FULL\PATH\TO\THIS\PROJECT\data\:/data
```
