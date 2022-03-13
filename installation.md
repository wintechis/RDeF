# Installation Guide

0. Open a terminal. In Windows, we recommend to use PowerShell.
   
1. Kivy momentarily does not support Python 3.10 yet. This is why Python 3.9 is the version to go for running RDeF. 
First, make sure that you have installed Python 3.9. Any patch version is fine. In the example below the patch version is 0.
```console
$ python --version
Python 3.9.0
```

2. Clone the GitHub Repository of RDeF. (Alternatively, you can download and extract a .zip archive.) 
```console
$ git clone "https://github.com/RDFLib/rdflib.git"
```

3. Move to the respective folder and create a virtual environment.
```console
$ cd RDeF
$ python -m venv  .
```

4. Activate the virtual environment and execute the main file to start the Demo story in RDeF. 
   
(Windows)
```console
$ scripts/activate
(RDeF) $ python main.py
```

(Linux)
```console
$ source    scripts/activate
(RDeF) $ python    main.py 
```


## Requirements
* Kivy 2.0.0 for creating the graphical user interface
* rdflib for managing Linked Data
* Pygments for highlighting RDF and SPARQL code (included in Kivy)
* PrettyTable for plotting query results in ASCII Tables (Upcoming)

Note: all packages might have additional requirements that are not listed here.


## Installation Errors and Reporting Bugs
If any error occurred while following the installation guide, please check the "Issues" list for an available solution. If your issue is new and you need help to resolve it, create an issue with a fitting title that starts with "Installation / ". 
