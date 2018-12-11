#!/bin/bash

#delete the file uploaded to the server for fixing after processing it

FILENAME=$2
DIRECTORY=$1
DIRECTORY+=$FILENAME
rm "$DIRECTORY"
