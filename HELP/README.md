# HELP: Configuration-aware Approach
To use HELP, you can run the command:
```
python3 fix.py <install_req> <tofile>
```
- *install_req* refers to the installation requirement,such as 'pro#ver#pyver', where pro is the name of the package, ver is the version of the package, and pyver is the required Python version.
- *tofile* refers to a **.json** file that store the installation solution if there is installation failure, such as 'result.json'

HELP supports the diagnosis of package installation in PyPI and Python version 3.3+.

## test

you can run the **test.py** to see the result. 



<!-- And it is easy to add other configuration files. -->