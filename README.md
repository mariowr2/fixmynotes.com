# Fixmynotes.com

This flask webapp  attempts to do away with "n slides in a single slide" notes sometimes used by university professors. It is particularly painful to zoom n times per page in order to study! Just upload the pdf you wish to transform into single slide per page document. See the files in ```example_input_and_output``` to see what I mean by "n slides in a single slide". The webapp can be used [here](http://fixmynotes.com). The project can also be used locally with more flexibility in this [repository.](https://github.com/mariowr2/PDF_Splitter).

## Local Setup
To setup the project, give execution permission to ```setup.sh```  by running ```$ chmod +x setup.sh``` and then run the script```$ ./setup.sh```. This script creates a virtual environment and installs all dependencies. Note that OpenCV 2 must be installed previously for the setup to be complete, I used this [script](https://gist.github.com/arthurbeggs/06df46af94af7f261513934e56103b30) to install OpenCV on Ubuntu 16.04. To run the program and the debug server locally run the following command:
```$ python __init__.py DEBUG```


