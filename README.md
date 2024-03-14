# Protein Feature Extraction

This repository contains the code for the creation of the Fondant pipeline that extracts protein features from protein sequences.

## Table of Contents

- [Installation](#installation)
- [Generation of Mock Data](#generation-of-mock-data)
- [Executing the pipeline](#executing-the-pipeline)
  - [Local](#local)
- [Partition issue with Fondant](#partition-issue-with-fondant)

## Installation

To install the pipeline, you need to run the following command to install the requirements file:

```bash
pip install -r requirements.txt
```

## Generation of Mock Data

**This section will be removed once mock data is no longer needed.**

Currently there is no specific data to test the pipeline, so to generate some mock data, a script was created for this purpose. The script is located in the `utils` folder and is called `generate_mock_data.py`. This file contains a basic object with a sequence and a name feature. You need to run the script to generate the mock data file, so it can be used in the pipeline.

Before you do this, you need to make sure that there is a ``data`` folder in the root of the project. This is the location where the ``mock_data.parquet`` file will be placed.

To execute this script, you need to run the following command:

```bash
python utils/generate_mock_data.py
```

## Executing the pipeline

### Local

Head over to the `README` file of the [local_pdb_component](./components/local_pdb_component/README.md) and follow the instructions to execute the pipeline locally.

## Partition issue with Fondant

If you look at the code in the `pipeline.py` file, you will see that the `iFeatureOmega_component` has an additional parameter that is called ``input_partition_rows``. This parameter is used to specify the number of rows that the input file will be partitioned into.

Fondant uses Dask to read the input file. Dask splits each partition into a different Pandas DataFrame. This is useful when you have a large file and you want to process it in parallel. However, with the iFeatureOmega component this for some reason causes an error. The error is related to the fact that the input file is partitioned into multiple files and the iFeatureOmega component is not able to find certain columns. This is a known issue and it is being addressed by the Fondant team.

For now, the workaround is to set the ``input_partition_rows`` parameter to the amount of rows inside the dataset, which in my case is 5 (test data). This will force Dask to make a partition for each row, which is not ideal, but it is the only way to make it work for now.
