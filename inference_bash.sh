#!/bin/bash

# Activate the conda environment
# CONDA_DIR=$(dirname $(which conda))
# source $CONDA_DIR/activate
# conda activate sadtalker

# Run the Python script
rm -rf results/*

#SBIRT
# python inference.py --driven_audio output.wav --source_image zimmerman/oldman_demo1.jpeg --facerender pirender --size 256 --batch_size 32

#Forensic Nursing
# python inference.py --driven_audio output.wav --source_image forensic_nursing/img1.jpeg --facerender pirender --size 256 --batch_size 32 --still

#Mock Trial
# python inference.py --driven_audio output.wav --source_image court_prosecutor.jpeg --facerender pirender --size 256 --batch_size 32
python inference.py --driven_audio output.wav --source_image court_prosecutor.jpeg --size 256


