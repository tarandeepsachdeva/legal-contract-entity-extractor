#!/bin/bash
source /opt/anaconda3/etc/profile.d/conda.sh
conda activate spacy_train
python "$1" "$2"
