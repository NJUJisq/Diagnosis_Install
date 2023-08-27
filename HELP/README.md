# HELP: Configuration-aware Approach
To use HELP, you can run the command:
```
python3 fix.py <install_req> <tofile>
```
- *install_req* refers to the installation requirement,such as 'pro#ver#pyver', where pro is the name of the package, ver is the version of the package, and pyver is the required Python version.
- *tofile* refers to a **.json** file that store the installation solution if there is installation error, such as 'result.json'

HELP supports the diagnosis of package installation in PyPI and Python version 3.3+.

<!-- And it is easy to add the support for the check for more Python versions by setting the 'py_install_versions' parameter in utils/sort_version.py. -->

## test

You can run the **test.py** to see the results (the generated solution is stored in the *result* folder by default). 



