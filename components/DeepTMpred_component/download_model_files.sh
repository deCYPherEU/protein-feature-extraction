#!/bin/bash

orientation_path="https://zenodo.org/record/5163061/files/deepTMpred-b.pth"
deeptmpred_path="https://zenodo.org/record/5163061/files/orientaion-b.pth"

if [ ! -d "src/model_files" ]; then
  mkdir -p src/model_files
fi

wget -P src/model_files "$orientation_path"
wget -P src/model_files "$deeptmpred_path"

echo "All model files are downloaded successfully!"
