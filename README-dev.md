Environment And Dependencies
----------------------------

Before you run the application, install the Python requests and the Flask libraries in your environment.  The needed requirements are listed in requirements.txt, so you can use pip:

    $ pip install -r requirements.txt


Testing
-------

In order to make sure the application passes the unit tests, install pytest and mock in your environment, or run:

    $ pip install -r test-requirements.txt


Then run:

    $ py.test ./tests


Running
-------

you can run the application under flask:

    $ FLASK_APP=/path/to/src/mytest/main.py flask run


The application will work with the default configuration: debug mode is "on", logging goes to the standard error, and no persistent storage for the database.  Run with a custom configuration:

    $ FLASK_APP=/path/to/src/mytest/main.py \
        MYTEST_CONFIGFILE=/path/to/src/mytest.conf \
        flask run

check out the `_default_config` in the src/mytest/main.py for the available configuration settings.  The configuration file must have the equivalent json structure.
