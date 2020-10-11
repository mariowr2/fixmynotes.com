# Fixmynotes.com
 

This flask webapp  attempts to do away with "n slides in a single slide" notes sometimes used by university professors. It is particularly painful to zoom n times per page in order to study! Just upload the pdf you wish to transform into single slide per page document. See the files in ```example_input_and_output``` to see what I mean by "n slides in a single slide". The webapp can be used at http://fixmynotes.com . You can find more information at my personal [website](https://mariomendez.me/projects/2018/12/16/fixmynotes.html).

# Demo
![](fixmynotes-demo.gif)

## Windows users
This program runs on Ubuntu. If you are on windows, [install the Windows Subsystem for Linux](https://ubuntu.com/wsl).

## Run the project locally
This program runs on python2.7 . Before running `setup.sh` ensure this path exists in your system `/usr/bin/python2.7`. You can do so by running the following comand:
~~~~
$ /usr/bin/python2.7
~~~~
If the python console comes up, then your python installation is in the correct place. If your python installation is not on `/usr/bin/python2.7`, change the following line from `setup.sh` to point to your installation location:
~~~
#change this line if necessary 
virtualenv virtual_env --python=/usr/bin/python2.7 
~~~

Once you know your python installation location is correct, run ```setup.sh```:
~~~~
$ sudo ./setup.sh
~~~~
```setup.sh``` script creates a virtual environment and installs all dependencies. The script will take some time because it builds OpenCV.  Once the script is done, activate the virtual environment created by the setup script :
~~~~
$ source virtual_env/bin/activate
~~~~
The virtual environment creates an isolated environment where only the project's dependencies exist.  
Now the program and debug server can be run locally :
~~~~
$ python __init__.py DEBUG
~~~~

## Contributors
* Big thanks to [Nico Connor](https://github.com/Nicolas-Connor)!