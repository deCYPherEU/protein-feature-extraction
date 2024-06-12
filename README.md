# Protein Feature Extraction

<p align="center">
    <img src="./assets/protein-sequences-ai.png" style="height:300px; width:300px; border-radius: 15%;" />
</p>

This repository contains the code for the creation of the Fondant pipeline that extracts protein features from protein sequences.

## Table of Contents

- [Protein Feature Extraction](#protein-feature-extraction)
  - [Table of Contents](#table-of-contents)
  - [Components](#components)
  - [Installation](#installation)
  - [Fondant](#fondant)
  - [Requirements](#requirements)
    - [Env variables](#env-variables)
      - [predict\_protein\_3D\_structure\_component](#predict_protein_3d_structure_component)
      - [unikp\_component](#unikp_component)
    - [Data files](#data-files)
  - [Google Cloud Credentials](#google-cloud-credentials)
  - [Executing the Pipeline](#executing-the-pipeline)
  - [Generation of Mock Data](#generation-of-mock-data)
  - [Partition issue with Fondant](#partition-issue-with-fondant)

## Components

This section contains the components that are used in the pipeline. Each component has its own README file that contains information about the component and how to set it up.

- [Biopython](./components/biopython_component/README.md)
- [Generate Protein Sequence Checksum](./components/generate_protein_sequence_checksum_component/README.md)
- [iFeatureOmega](./components/iFeatureOmega_component/README.md)
- [Filter PDB](./components/filter_pdb_component/README.md)
- [Predict Protein 3D Structure](./components/predict_protein_3D_structure_component/README.md)
- [MSA](./components/msa_component/README.md)
- [Peptide](./components/peptide_features_component/README.md)
- [DeepTMpred](./components/DeepTMpred_component/README.md)
- [Store PDB](./components/store_pdb_component/README.md)
- [UniKP](./components/unikp_component/README.md)
- [PDB Features Component](./components/pdb_features_component/README.md)

## Installation

To install the pipeline, you need to run the following command to install the requirements file:

```bash
pip install -r requirements.txt
```

Make sure you have Docker installed on your machine. You can download it [here](https://www.docker.com/products/docker-desktop). Check your Docker version and make sure it is at least `24.0.0`.

## Fondant

This project uses Fondant to run the pipeline.

Fondant is a tool that allows you to run your pipeline in a containerized environment. This is useful because it allows you to run your pipeline in a consistent environment, regardless of the operating system you are using.

## Requirements

This section will go over the requirements needed to run the pipeline.

### Env variables

There are some environment variables that need to be set in order to run the pipeline. These are the following:

#### predict_protein_3D_structure_component

```bash
HF_API_KEY=""
HF_ENDPOINT_URL=""
```

#### unikp_component

```bash
HF_API_KEY=""
HF_ENDPOINT_URL=""
```

Place the `.env` file in the component folder where the component is located. Make sure this file is in the same level as the `Dockerfile`, `fondant_component.yaml`, and `requirements.txt` files.

### Data files

The pipeline will mount to the specified folder when executing the pipeline. This is done by using the `--extra-volumes` flag when running the pipeline.

The data folder should contain the following files:

- `mock_data.parquet`
  - see [Generation of Mock Data](#generation-of-mock-data) for more information
- `google_cloud_credentials.json`
  - see [Filter PDB Component](./components/filter_pdb_component/README.md) for more information
- `protein_smiles.json`
  - see [uniKP Component](./components/unikp_component/README.md) for more information

It should also contain the following folders:

- `pdb_files`
  - see [Filter PDB Component](./components/filter_pdb_component/README.md) for more information

For the `deepTMpred_component`, you'll firstly need to download the models used in the component. Starting from the [component itself](./components/DeepTMpred_component/), run the following command:

```bash
bash download_model_files.sh
```

The reason why this isn't done in the Dockerfile is because the models are quite large and take up a lot of space. This way, you don't need to download them every time you build the Docker image. A full explanation of the component can be found [here](./components/DeepTMpred_component/README.md).

## Google Cloud Credentials

The components `filter_pdb_component` and `store_pdb_component` have an option to load in pdb files from Google Cloud Storage. In order to do this, you need to have a Google Cloud Service Account key. This key should be placed in the `data` folder. You can choose the naming, but you'll have to modify the component arguments in `pipeline.py`.

## Executing the Pipeline

You can execute the following command to run the pipeline in your terminal:

```bash
PS> fondant run local pipeline.py --extra-volumes YOUR/FULL/PATH/TO/THIS/PROJECT/data:/data
```

## Generation of Mock Data

Currently there is no specific data to test the pipeline, so to generate some mock data, a script was created for this purpose. The script is located in the `utils` folder and is called `generate_mock_data.py`. This file contains a basic object with a sequence and a name feature. You need to run the script to generate the mock data file, so it can be used in the pipeline.

Before you do this, you need to make sure that there is a `data` folder in the root of the project. This is the location where the `mock_data.parquet` file will be placed.

To execute this script, you need to run the following command:

```bash
python utils/generate_mock_data.py
```

## Partition issue with Fondant

If you look at the code in the `pipeline.py` file, you will see that the `iFeatureOmega_component` has an additional parameter that is called `input_partition_rows`. This parameter is used to specify the number of rows that the input file will be partitioned into.

Fondant uses Dask to read the input file. Dask splits each partition into a different Pandas DataFrame. This is useful when you have a large file and you want to process it in parallel. However, with the iFeatureOmega component this for some reason causes an error. The error is related to the fact that the input file is partitioned into multiple files and the iFeatureOmega component is not able to find certain columns. This is a known issue and it is being addressed by the Fondant team.

For now, the workaround is to set the `input_partition_rows` parameter to the amount of rows inside the dataset, which in my case is 5 (test data). This will force Dask to make a partition for each row, which is not ideal, but it is the only way to make it work for now.
