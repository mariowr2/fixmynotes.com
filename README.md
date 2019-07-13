# Fixmynotes.com

This flask webapp  attempts to do away with "n slides in a single slide" notes sometimes used by university professors. It is particularly painful to zoom n times per page in order to study! Just upload the pdf you wish to transform into single slide per page document. See the files in ```example_input_and_output``` to see what I mean by "n slides in a single slide". The webapp can be used at http://fixmynotes.com . You can find a demo of the app in my personal [website](https://mariomendez.me/projects/2018/12/16/fixmynotes.html).

## Run the program and server locally
To setup the project, give execution permission  ```setup.sh``` :
~~~~
$ chmod +x setup.sh
~~~~
Then run ```setup.sh```:
~~~~
$ sudo ./setup.sh
~~~~
```setup.sh``` script creates a virtual environment and installs all dependencies. Note that OpenCV 2 must be installed previously for the setup to be complete, I used this [script](https://gist.github.com/arthurbeggs/06df46af94af7f261513934e56103b30) to install OpenCV on Ubuntu 16.04.  

Before running the program, activate the virtual environment created by the setup script :
~~~~
$ source virtual_env/bin/activate
~~~~
The virtual environment creates an isolated environment where only the project's dependencies exist.  
Now the program and debug server can be run locally :
~~~~
$ python __init__.py DEBUG
~~~~
