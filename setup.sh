#!/bin/bash

echo "Creating virtual environment..."
sudo apt-get install python-pip
sudo pip install virtualenv
virtualenv virtual_env --python=/usr/bin/python2.7 #this line assumes /usr/bin/python2.7 exists
source virtual_env/bin/activate
echo "Done"

echo "Installing dependencies..."
sudo apt install poppler-utils
sudo apt-get install libjpeg8-dev #this file is something missing
pip install pillow
pip install pdf2image
pip install reportlab
pip install numpy
echo "Done"
# actual backend dependencies
pip install Flask
pip install Werkzeug


echo "Done"

echo "Linking cv.so to virtual environment..."
echo " " > requirements.txt
make
rm requirements.txt
echo "Finished setup"
