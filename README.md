# Protein Feature Extraction

This repository contains the code for the creation of the Fondant pipeline that extracts protein features from protein sequences.

**This readme is still a work in progress.**

## Installation

To install the pipeline, you need to run the following command to install the requirements file:

```bash
pip install -r requirements.txt
```

This will generate a file named mock_data.parquet in the data folder. This file will be used to test the pipeline.

## Generation of Mock Data

**This section will be removed once mock data is no longer needed.**

Currently there is no specific data to test the pipeline, so to generate some mock data, a script was created for this purpose. The script is located in the `utils` folder and is called `generate_mock_data.py`. This file contains a basic object with a sequence and a name feature. You need to run the script to generate the mock data file, so it can be used in the pipeline.

To execute this script, you need to run the following command:

```bash
python utils/generate_mock_data.py
```

## Adding the iFeatureOmega repo to the iFeatureOmega_component folder

iFeatureOmega is a GitHub repo that contains the code for the iFeatureOmega tool. This tool is used to extract protein features from protein sequences. It sadly doesn't have a pip package, so we need to add the repo to the iFeatureOmega_component folder. To do this, you need to run the following command:

```bash
git clone https://github.com/Superzchen/iFeatureOmega-CLI

# linux users
mv iFeatureOmega iFeatureOmega_component

# windows users
Move-Item -Path iFeature -Destination components/iFeatureOmega_component/src/
```

## Executing the Pipeline

For Windows users, you need to run the following command to execute the pipeline:

```bash
PS> fondant run local pipeline.py --extra-volumes YOUR\FULL\PATH\TO\THIS\PROJECT\data:/data
```
