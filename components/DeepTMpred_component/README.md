# DeepTMpred Component

DeepTMpred is a deep learning-based method for predicting transmembrane helices in proteins. The GitHub repository for the DeepTMpred method can be found [here](https://github.com/ISYSLAB-HUST/DeepTMpred).

## Usage

To use the DeepTMpred component, you will need to download the necessary models. These models are crucial for the component to work, but require a large amount of storage space (~350MB). To download the models, run the following command:

```bash
# assuming your terminal starts in the components/DeepTMpred_component directory
bash download_model_files.sh
```

This script will download the models and place them in the `./src/model_files` directory. Once the models are downloaded, you can use the component as normal by applying this component to the dataset in the `pipeline.py` file.
