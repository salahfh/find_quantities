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
* Activate the virtual enviroment `.\venv\Scripts\activate` 
* Install package from repo: `pip install git+https://github.com/salahfh/find_quantities.git`


## Update
With the new version, run `find_quantity -u` to automatically update. 

Alternatively, manual updating is supported via the steps below:
* Open `PowerShell` from windows start menu
* Change to the folder `cd bin`
* Activate the virtual enviroment `.\venv\Scripts\activate`
* Run the command to update: `pip install git+https://github.com/salahfh/find_quantities.git`


## Usage
To use the program follow these steps below
* Open a `PowerShell` window from windows start menu
* Change to the folder `cd bin`
* Activate the virtual enviroment `.\venv\Scripts\activate`
* Run the command `find_quantity` and follow the instructions if it doesn't work run `python -m find_quantity`


### Flags/Options
* `-h`: display the help menu
* `-v`: prints out the software version
* `-u`: perform update of the software to the latest version in the repo
* `-y YEAR`: specify the year of the data for the final date generation. The default is 2024.


## Merge Rules
The program offer different ways to merge the products together as package. A template file is automatically 
created at the start of new project. In order to work effectively with the config `merge_product_rules.yml`,
there  are few rules to keep in mind: 
* The YAML (`.yml`) is sensitve to indentations and white spaces.
* The structure of the file sections must be followed as specified in the default template. 
* The available commads are: 
    1. `AutoMergeIOProducts`: auto merge all products tags (`n_article`) ending with `-I` or `-O` 
    2. `CombineProducts`: takes a list of products under the section `packages` and merge them together
    3. `MergeBasedOnPattern`: search for products tags (`n_article`) matching the regex `pattern` and
       combines them with the `products` section under `packages`. Multiple `packages` with one or 
        more `products` can be defined at the same time. 

**WARNING**: Special attention must be paid to the `pattern` to avoid matching against the wrong products. 
For pattern testing, the website [regex](https://regexr.com/) is very useful.



## Issues
### `find_quantity` not found
After following the steps to install the program, there's no error at this stage, but when you run try to run the program using `find_quantity` you get an error. Try to run it with `python -m find_quantity` instead. This issue might be due the package has not been added to your `PowerShell` path. This could be due to virtual environment not activated correctly for some reason (venv not showing in green in the command prompt). 


