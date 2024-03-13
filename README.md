# Protein Feature Extraction

This repository contains the code for the creation of the Fondant pipeline that extracts protein features from protein sequences.

## Table of Contents

- [Installation](#installation)
- [Generation of Mock Data](#generation-of-mock-data)
- [Hugging Face Endpoint Component](#hugging-face-endpoint-component)
  - [Installing Nimbus](#installing-nimbus)
  - [Installing Terraform](#installing-terraform)
  - [Installing Google Cloud SDK](#installing-google-cloud-sdk)
  - [Getting Google Cloud Credentials](#getting-google-cloud-credentials)
  - [Creating the environment file](#creating-the-environment-file)
- [Creating the Infrastructure](#creating-the-infrastructure)
- [Executing the Pipeline](#executing-the-pipeline)
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

## Hugging Face Endpoint Component

The Hugging Face Endpoint component is a custom component that is used to interact with the Interface Endpoints of the Hugging Face API. This component is used to predict the tertiary structure of a protein sequence using the ESMFold model. The Hugging Face component makes use of the Nimbus tool to create the infrastructure on the Google Cloud Platform to store the created pdb files. The component also uses the Google Cloud SDK to authenticate with the Google Cloud Platform.

> path: [hf_endpoint_component](./components/hf_endpoint_component/)

The following sections contain the requirements for the component and the installation steps.

### Installing Nimbus

Nimbus is a tool created by ML6. This project is used to generate boilerplate code for cloud providers. To install Nimbus, you need to run the following command:

> Make sure you have access to the ML6 Bitbucket repository.

```bash
pip install git+https://USERNAME:APP_PWD@bitbucket.org/ml6team/nimbus.git#egg=Nimbus
```

After installing, make sure to run the following command to configure the tool:

```bash
# create a new directory for the nimbus project
mkdir nimbus
cd nimbus

nimbus gcp init

# fill in the required information
```

### Installing Terraform

Nimbus uses Terraform to create the infrastructure. To install Terraform, you need to run the following steps:

1. Download the Terraform binary from the [official website](https://developer.hashicorp.com/terraform/install)
2. Extract the binary to a folder that is in your PATH
3. Run the following command to verify the installation:

```bash
terraform --version
```

### Installing Google Cloud SDK

Nimbus uses the Google Cloud SDK to interact with the Google Cloud Platform. To install the Google Cloud SDK, you need to run the following steps:

1. Download the Google Cloud SDK from the [official website](https://cloud.google.com/sdk/docs/install)
2. Run the installer and follow the instructions
3. Run the following command to verify the installation:

```bash
gcloud --version
```

After all of these steps, you should have a working Nimbus installation.

### Creating the Infrastructure

When setting up a new project with Nimbus, you need to create the infrastructure. Nimbus creates a terraform folder terraform/backend for the remote Terraform state and versioning. This has to be run first and will create a GCS bucket on your project. Run the following steps:

```bash
cd terraform/backend
terraform init
terraform plan --var-file ../environment/project.tfvars 
terraform apply --var-file ../environment/project.tfvars
```

Then you can initialize the project using the main terraform configs:

```bash
cd ..
cd terraform/main
terraform init
terraform plan --var-file ../environment/project.tfvars 
terraform apply --var-file ../environment/project.tfvars
```

### Getting Google Cloud Credentials

To use the Google Cloud SDK, you need to authenticate with your Google Cloud account. To do this, you need to run the following command:

```bash
gcloud auth application-default login
```

This command should create a new browser window where you can authenticate with your Google Cloud account. It also create a new file in your home directory called ``.config/gcloud/application_default_credentials.json``. This file contains the credentials that are used to authenticate with the Google Cloud SDK.

### Creating the environment file

The environment file is used to store the project information. This file is used by the component to for access to the Google Cloud Platform and the Hugging Face Interface Endpoints. This file looks as follows:

```js
HF_API_KEY=huggingface-api-key
HF_ENDPOINT_URL=huggingface-endpoint-url
PROJECT_ID=project-id
BUCKET_NAME=bucket-name
GOOGLE_APPLICATION_CREDENTIALS=google_cloud_credentials.json
```

This file should be placed in the ``hf_endpoint_component`` folder and should be called ``.env``.

The other file that should be added is the ``google_cloud_credentials.json`` file. This file is used to authenticate with the Google Cloud Platform. This file should also be placed in the ``hf_endpoint_component`` folder.

## Executing the Pipeline

### Local

Make sure you have a local copy of the parquet file containing the following columns: `sequence_id`, `pdb_string`. These don't need to contain any data, as the pipeline will generate the data for you, but the columns need to be present.

If there is any data present then you will need to keep in mind that the checksum operation is used on the ``sequence_id`` column. The checksum operation uses the sequences (string), which are not present in this file. Make sure to use the right checksum operation for your data. The following code shows you how to use the checksum operation on the sequence column:

```python
import Bio.SeqUtils.CheckSum.crc64
import pandas as pd

dataframe["sequence_id"] = dataframe["sequence"].apply(lambda x: Bio.SeqUtils.CheckSum.crc64(x))
```

If you want to execute the pipeline using local pdb files, you need to run the following command:

```bash
PS> fondant run local pipeline.py --extra-volumes YOUR\FULL\PATH\TO\THIS\PROJECT\data\pdb_file.parquet:/pdb_file.parquet
```

### Cloud

If you want to execute the pipeline using the cloud infrastructure for the pdb files, you can run the following command:

```bash
PS> fondant run local pipeline.py
```

## Partition issue with Fondant

If you look at the code in the `pipeline.py` file, you will see that the `iFeatureOmega_component` has an additional parameter that is called ``input_partition_rows``. This parameter is used to specify the number of rows that the input file will be partitioned into.

Fondant uses Dask to read the input file. Dask splits each partition into a different Pandas DataFrame. This is useful when you have a large file and you want to process it in parallel. However, with the iFeatureOmega component this for some reason causes an error. The error is related to the fact that the input file is partitioned into multiple files and the iFeatureOmega component is not able to find certain columns. This is a known issue and it is being addressed by the Fondant team.

For now, the workaround is to set the ``input_partition_rows`` parameter to the amount of rows inside the dataset, which in my case is 5 (test data). This will force Dask to make a partition for each row, which is not ideal, but it is the only way to make it work for now.
