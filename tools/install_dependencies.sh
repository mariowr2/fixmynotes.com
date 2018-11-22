#!/bin/bash

#dependencies for running the script

sudo apt install poppler-utils
pip install pdf2image
pip install reportlab
pip install numpy

# dependencies for webapp
pip install Flask
pip install Werkzeug


echo "Finished"
