# Filter PDB Component

The FilterPDBComponent is a component that takes in a dataframe and, based on the method given, it loads up the PDB files and keep the ones that don't exist yet. This component compares the existing PDB files with the ones in the dataframe using the checksum and filters out the ones that already exist. The methods are either 'local' or 'remote', where the 'local' version will use the PDB files in the provided directory and the 'remote' version will fetch the PDB files from the GCP Storage Bucket. The component returns the filtered dataframe and the PDB files that we already generated.

## Env Setup

The following arguments will need to be provided for this component in the `pipeline.py` file:

```yaml
    method:
        type: str
        description: "The method to use to fetch and save the PDB file. Can be 'local' or 'remote'."
        default: "local"
    local_pdb_path:
        type: str
        description: "The path to the PDB files. Only used when the method is 'local'."
        default: None
    bucket_name:
        type: str
        description: "The name of the GCP Storage Bucket. Only used when the method is 'remote'."
        default: None
    project_id:
        type: str
        description: "The GCP project ID. Only used when the method is 'remote'."
        default: None
    google_cloud_credentials_path:
        type: str
        description: "The path to the Google Cloud credentials file. Only used when the method is 'remote'."
        default: None
```

Make sure you have the `google_cloud_credentials.json` file in the `data` folder. This file is needed to access the GCP Storage Bucket. This file can be created using the following command:

```bash
# login
gcloud auth login

# generate the file
gcloud auth application-default login
```

The logs of that command will show you the path to the generated file.

- Linux/MacOS: `~/.config/gcloud/application_default_credentials.json`
- Windows: `C:\Users\USERNAME\AppData\Roaming\gcloud\application_default_credentials.json`
