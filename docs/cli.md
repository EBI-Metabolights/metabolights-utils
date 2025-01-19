# Installation

---
The following command installs metabolights-utils from the Python Package Index. You will need Python 3.8+ and pip3 on your operating system.

* (If python3 is not installed) Download and install [Python](https://www.python.org/downloads)
* (If pip3 is not installed) Install [pip3](https://pip.pypa.io/en/stable/installation) 
* Install metabolights-utils library
```shell
cd <directory to create a virtual environment>

# install metabolights-utils on new a virtual environment named mtbls-venv (you may change it)
python3 -m venv mtbls-venv
source mtbls-venv/bin/activate
pip install --upgrade pip
pip3 install -U metabolights-utils

# test mtbls command
mtbls --version
```