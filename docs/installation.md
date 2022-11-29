# Installation Guide

0. Open a terminal. In Windows, we recommend to use PowerShell.
   
1. RDeF runs with Python 3.10. 
First, make sure that you have installed Python 3.10. Any patch version is fine. In the example below the patch version is 8.
```shell
$ python --version
Python 3.10.8
```

1. Clone the GitHub Repository of RDeF. (Alternatively, you can download and extract a .zip archive.) 
```shell
git clone "https://github.com/wintechis/RDeF.git"
```

1. Move to the respective folder and create a virtual environment.
```shell
cd RDeF
python -m venv env
```

1. Activate the virtual environment and start RDeF. 
   
(Windows)
```shell
env/scripts/activate
python main.py
```

(Linux)
```shell
source  env/bin/activate
python    main.py 
```

If you want to run a specific story (here the demo) without entering the main menu, run:
```shell
python    main.py  --play demo
```

## Requirements
* Kivy 2.1.0 for creating the graphical user interface
* RDFLib for managing Linked Data
* Pygments for highlighting RDF and SPARQL code (included in Kivy)
* PrettyTable for plotting query results in ASCII Tables

```shell
pip install kivy==2.1.0 rdflib==6.2.0 prettytable==3.5.0
```

## Installation Errors and Reporting Bugs
If any error occurred while following the installation guide, please check the "Issues" list for an available solution. If your issue is new and you need help to resolve it, create an issue with a fitting title that starts with "Installation / ". 
