# Local PDB Component

The Local PDB component is a custom component that is used to generate the tertiary structure of a protein sequence using the ESMFold model. The Local PDB component makes use a local file as a cache for the pdb files.

## Environment Variables

The following environment variables are used in the Local PDB component:

```py
HF_API_KEY="YOUR_API_KEY"
HF_ENDPOINT_URL="YOUR_ENDPOINT_URL"
```

The arguments for this Fondant component require you to add a local parquet file containing the following columns: `sequence_id`, `pdb_string`. This file is accessed via the `--extra-volumes` argument. You will need to place this file in the `data` directory of the project.

The `config` file will direct Fondant to the right location of the files. If you place the file in a different location, you will need to change the `config` file accordingly.

## Executing the Pipeline

### Local

Make sure you have a local copy of the parquet file containing the following columns: `sequence_id`, `pdb_string`. These don't need to contain any data, as the pipeline will generate the data for you, but the columns need to be present.

If there is any data present then you will need to keep in mind that the checksum operation is used on the `sequence_id` column. The checksum operation uses the sequences (string), which are not present in this file. Make sure to use the right checksum operation for your data. The following code shows you how to use the checksum operation on the sequence column:

```python
import Bio.SeqUtils.CheckSum.crc64
import pandas as pd

dataframe["sequence_id"] = dataframe["sequence"].apply(lambda x: Bio.SeqUtils.CheckSum.crc64(x))
```

If you want to execute the pipeline using local pdb files, you need to run the following command:

```bash
PS> fondant run local pipeline.py --extra-volumes YOUR\FULL\PATH\TO\THIS\PROJECT\data\pdb_file.parquet:/pdb_file.parquet
```
