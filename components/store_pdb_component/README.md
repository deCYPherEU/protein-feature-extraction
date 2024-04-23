# Store PDB Component

The StorePDBComponent stores the PDB file given a method. This storage_type consists of two options 'local' and 'remote'. The 'local' storage_type is used to store the PDB file locally in the provided folder. The 'remote' storage_type will use the GCP storage bucket to store the PDB file.

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

Make sure you have the `google_cloud_credentials.json` file in the `data` folder. This file is needed to access the GCP Storage Bucket.
