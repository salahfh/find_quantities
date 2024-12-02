# Find Quantity

Program to help determine quantity of products for each Showroom.

## Setup
Follow the steps to install the software
* Install [Python](https://www.python.org/downloads/).
* Install [git](https://git-scm.com/downloads)
* Open `PowerShell` from windows start menu
* run `python --version` to confirm python is installed
* run `git --version` to confirm git is installed
* Make sure pip is installed. `pip --version`
* Create a new folder using the command `mkdir bin`
* Change to the newly created folder `cd bin`
* Create a virtual enviroment for python application `python -m venv venv`
* Activate the virtual enviroment `.\venv\Scripts\activate.bat` 
* Install package from repo: `pip install git+https://github.com/salahfh/find_quantities.git`


## Usage
To use the program follow these steps below
* Open a `PowerShell` window from windows start menu
* Change to the folder `cd bin`
* Activate the virtual enviroment `.\venv\Scripts\activate.bat`
* Run the command `find_quantity` and follow the instructions if it doesn't work run `python -m find_quantity`


## Update
In order to update the software follow the below steps
* Open `PowerShell` from windows start menu
* Change to the folder `cd bin`
* Activate the virtual enviroment `.\venv\Scripts\activate.bat`
* Run the command to update: `pip install git+https://github.com/salahfh/find_quantities.git`

## Issues
### `find_quantity` not found
After following the steps to install the program, there's no error at this stage, but when you run try to run the program using `find_quantity` you get an error. Try to run it with `python -m find_quantity` instead. This issue might be due the package has not been added to your `PowerShell` path. This could be due to virtual environment not activated correctly for some reason (venv not showing in green in the command prompt). 


