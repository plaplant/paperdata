## paperdata

*Module for building, searching, and updating the PAPER database compression pipeline*

-----
SETUP
-----

The preferred method for installing this package is to use anaconda, and then create a new environment for this package. These instructions assume that anaconda is already installed. If not, installation instructions can be found here: https://docs.continuum.io/anaconda/install.

The steps for installing are:

1. First, clone this repository onto the target machine:
    ```sh
    $ git clone https://github.com/plaplant/paperdata.git 
    ```
    This will create a new folder named `paperdata` in the target folder.

2. Modify the names of the configuration files:
    ```sh
    $ cd paperdata/config
    $ mv paperdata.cfg.test paperdata.cfg
    ````

    Perform this renaming for each configuration file. Also note that appropriate usernames, passwords,
    and hostnames for the MySQL databases need to be provided as well.

3. Set up a new anaconda environment:

    ```sh
    $ conda create -n paperdata python=2.7 anaconda
    ```
    
4. Activate the new environment:

    ```sh
    $ source activate paperdata
    ```

5. Install additional required packages using anaconda. `paperdata` requires `paramiko` and `mysql-python`:

    ```sh
    $ conda install paramiko mysql-python
    ```

6. Run python setup script and install locally. Make sure the following command is
executed from the directory above paperdata. For example:

    ```sh
    $ pwd
    ~/paperdata
    $ cd ..
    $ pip install ./paperdata
    ```
    
    This approach will keep the installation of the package local to the established python
    environment.

7. Check that everything is installed correctly by running a simple command from within python:

    ```python
    >>> from paper.data import dbi as pdbi
    >>> dbi = pdbi.DataBaseInterface()
    ```
    If all has gone well (including configuring the database config files), then there should be no errors returned.

8. Further setup required if running docker container or rebuilding database. Also note that
the anaconda environment must be activated in each new instance prior to using this package.

-----------
DESCRIPTION
-----------

## paper
```
Main package for modules
```

### data
```
Contains modules which directly interact with the paperdata database
```

### distiller
```
Contains modules which directly interact with the paperdistiller database
```

### ganglia
```
Contains modules to record the state of each host at any time in the ganglia database
```

### calibrate
```
module & scripts for calibration of uv files
NOW DEFUNCT
```

## heralive
```
module & scripts for instantiation of websites for paperdata
```

-------------
EXAMPLE QUERY
-------------
*Example of how to get all compressed files in database in a certain range julian days and change field is_tapeable to True*
```js
from paper.data import dbi as pdbi

dbi = pdbi.DataBaseInterface() <!--instantiate DBI object-->
with dbi.session_scope() as s: <!--instantiate session object as context manager-->
	FILE_query = s.query(pdbi.File).join(pdbi.Observation) <!--grabs base query object and joins table-->
	<!--filters query to look for particular range of dates and a file type-->
	filtered_query = FILE_query.filter(pdbi.File.filetype == 'uvcRRE')\
							   .filter(pdbi.Observation.julian_day >= 2455903)
							   .filter(pdbi.Observation.julian_day <= 2456036)
	FILEs = filtered_query.all() <!--gets generator of all FILE objects-->
	for FILE in FILEs:
		FILE.is_tapeable = True
	<!--automatically commits to database upon finishing due to context manager-->
```

-------
LICENSE
-------
```
GPL. Inside LICENSE file
```
