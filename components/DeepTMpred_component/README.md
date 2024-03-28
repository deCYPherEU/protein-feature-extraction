# DeepTMpred Component

DeepTMpred is a deep learning-based method for predicting transmembrane helices in proteins. The GitHub repository for the DeepTMpred method can be found [here](https://github.com/ISYSLAB-HUST/DeepTMpred).

## Usage

To use the DeepTMpred component, you will need to download the necessary models. These models are crucial for the component to work, but require a large amount of storage space (~350MB). To download the models, run the following command:

```bash
# assuming your terminal starts in the components/DeepTMpred_component directory
bash download_model_files.sh
```

This script will download the models and place them in the `./src/model_files` directory. Once the models are downloaded, you can use the component as normal by applying this component to the dataset in the `pipeline.py` file.

## DeepTMpred

The DeepTMpred component is a deep learning-based method for predicting transmembrane helices in proteins. The component takes a dataset of protein sequences as input and returns a dataset with.

## How does this component work?

Each protein sequence int the dataset is taken and used as input to the DeepTMpred model. The model then predicts the transmembrane helices in the protein sequence and returns a json object with the results. The results are then added to the dataset and returned.

### Results

The DeepTMpred model creates a `test.json` file with the contents of that file being the topology of the protein sequence. This topology describes where the transmembrane helices are located in the protein sequence.

The following features are generated from this topology:

```yaml
tmh_num_helices: The number of transmembrane helices in the protein sequence.
tmh_total_length: The total length of the transmembrane helices in the protein sequence.
tmh_avg_length_total: The average length of the transmembrane helices in the protein sequence.
tmh_biggest_length: The length of the biggest transmembrane helix in the protein sequence.
tmh_smallest_length: The length of the smallest transmembrane helix in the protein sequence.
```