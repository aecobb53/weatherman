# Weatherman Testing

## Table of contents

Backend
- [Functional](#functional)
    - [Running](#running)
    - [Features](#features)
    - [Steps](#steps)
    - [Data Validation]{#data-validation}
- [Unit](#unit)
    - [Running](#running)
    - [Tests](#tests)

Frontend
- [uhhh...](#uhhh)

## Functional

The functional tests are run with Behave. 
They have two main parts, the [features](/features) and the [steps](/features/steps). 
The features are supposed to be somewhat human readable to know what the test is doing. 
The steps take the features and run the backend code to test it. 

[Back to top](#table-of-contents)

### Running

In Docker:

`docker-compose up [--build] test`

In terminal (this is fine to run wherever as long as you have `behave` installed). 
Make sure you are in the man directory. 
Sadly I havnt found a good way to pass arguments to the behave testing so I update the 
`docker-compose.yml` file when I dont want to run everything. 

`behave` - Full behave run

`behave features/<feature file>` - Single feature run

`behave features/<feature file>:<line number of scenario>` - Single scenario in a feature. 
While it seems to be fine if the line number is anywhere in the scenario, its easiest if you try to 
get the line where the scenario starts. 

### Features

There are different before and after setup/teardown events for each Feature and Scenario. 
They are run from the `environment.py` file in steps. 

Before each behave testing session the testing database is deleted and the old logging files are archived. 
After each testing session the testing database is deleted as well. 

There are not currently feature setup/teardown. 

For each scenario you can add `@DEBUG`, `@INFO`, or `@WARNING` tags to set the console logging level for the scenario. 
By default the logging level for file/console is DEBUG/WARNING. 
This makes it easy to run tests but see detailed readouts for whats desired. 
I tried to have the Then scenarios return info but the rest return debug. 
Logging is handled in the `steps_logging.py` wrapper of the logger class. 
At the end of each scenario the logging is reset back to WARNING. 

- [Weather Butler](#weather-butler)
- [SQL Butler](#sql-butler)

##### Weather Butler

The major tags for the weather butler feature are `owma` and `on`/`off`. 
the owma stands for Open Weather Map api. 
It is the tag for the website functional tests. 
The on/off flags are used to turn on and off polling the database in the `environment.py` file. 
Because there is a limited number of polls you can use per month with the free subscription it made sense to add a limiter. 
If you dont have either it will assume on. 

Tests:

- Generating a poll url
    - Does the database set up a properly formatted url for the requests module?
- Successful poll
    - Does the response module get a proper response?
- weather butler poll function
    - Does the poll function do everything it needs to?
- data returned is formatted correctly
    - Does the data formatter module return valid data 

> Still need negative tests

##### SQL Butler

The major tags for sql butler is `@database`. 
For each database scenario I delete the testing databases. 

- Creating a sql database
    - Does the database set up and accept perfect data?
- Adding multiple weather reports to database
    - Does the database take a list of weather and return the list?
- Tuple to dict
    - Does the tupe to dict function work properly?
- List of tuples to list of dicts
    - Does the list tuple to list dict function work properly?
- Use parameters to return results from the database
    - Does the database take a list of weather and return the list?

> Still need negative tests

##### Data Validation

The major tags for sql butler is `@validator`. 
Verify the data validator interprits the input strings appropriatly. 

- Exact_list
    - Does the validator handle the exact list types appropriatly?

- Datetime validator
    - Does the validator handle the datetime strings appropriatly?

> Still need negative tests

### Steps


## Unit

I use pytest to run the unit tests. 
I started writing them but did not finish. 
There is still alot to do. 

[Back to top](#table-of-contents)

### Running

`docker-compose run unit-test sh`

in sh terminal `pytest` or `pytest -k <name>`

### Tests

## uhhh

I dont know how to run frontend tests. 
I will get to it eventually. 

[Back to top](#table-of-contents)
