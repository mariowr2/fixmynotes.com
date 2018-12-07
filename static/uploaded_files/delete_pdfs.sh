#!/bin/bash

#delete the uploaded file

FILENAME=$1
DIRECTORY="uploaded_files/" 
DIRECTORY+=$FILENAME
rm "$DIRECTORY"
