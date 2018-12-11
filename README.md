# PDF_Splitter_web

This flask webapp  attempts to do away with "4 slides in a single slide" notes sometimes used by university profesors. It is particularly painful to zoom 4 times per slide in order to study! Just upload the pdf you wish to transform into single slide per page document. See the files in ```example_input_and_output``` to see what I mean by "4 slides in a single slide". The webapp can be used [here](http://fixmynotes.com). The project can also be used locally with more flexibility in this [repository.](https://github.com/mariowr2/PDF_Splitter).

## Local Setup
To setup the project, give execution permission to ```setup.sh``` ```$ chmod +x setup.sh``` and then run the script```$ ./setup.sh```. This script creates a virtual environment and installs all dependencies. Note that OpenCV must be installed previously for the setup to be complete. To run the program in localhost, the variables at the top of ```__init__.py``` such as ```app.root_path``` will have to change so that they match the path of where the program is.


