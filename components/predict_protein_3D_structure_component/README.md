# Predict Protein 3D Structure Component

The PredictProtein3DStructureComponent is a component that takes in a dataframe and sends the sequences to the HuggingFace ESMFold Endpoint to predict the tertiary structures of the proteins. The component returns the dataframe with the predicted tertiary structures.

## Env Setup

You'll need to add a `.env` file in the component folder with the following environment variables:

```bash
HF_API_KEY=""
HF_ENDPOINT_URL=""
```
