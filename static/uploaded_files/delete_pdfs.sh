#!/bin/bash

#delete the file uploaded to the server for fixing after processing it

FILENAME=$1
DIRECTORY="/var/www/Fix/Fix/static/uploaded_files/" 
DIRECTORY+=$FILENAME
rm "$DIRECTORY"
