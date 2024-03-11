# Protein Feature Extraction

This repository contains the code for the creation of the Fondant pipeline that extracts protein features from protein sequences.

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

## Installing Nimbus

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

## Executing the Pipeline

For Windows users, you need to run the following command to execute the pipeline:

```bash
PS> fondant run local pipeline.py --extra-volumes YOUR\FULL\PATH\TO\THIS\PROJECT\data:/data
```

## Partition issue with Fondant

If you look at the code in the `pipeline.py` file, you will see that the `iFeatureOmega_component` has an additional parameter that is called ``input_partition_rows``. This parameter is used to specify the number of rows that the input file will be partitioned into.

Fondant uses Dask to read the input file. Dask splits each partition into a different Pandas DataFrame. This is useful when you have a large file and you want to process it in parallel. However, with the iFeatureOmega component this for some reason causes an error. The error is related to the fact that the input file is partitioned into multiple files and the iFeatureOmega component is not able to find certain columns. This is a known issue and it is being addressed by the Fondant team.

For now, the workaround is to set the ``input_partition_rows`` parameter to the amount of rows inside the dataset, which in my case is 5 (test data). This will force Dask to make a partition for each row, which is not ideal, but it is the only way to make it work for now.
