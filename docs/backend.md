# Weatherman backend

## Table of contents

- [Docker](#docker)
- [SQLite](#sqlite)
- [Technical breakdown](#technical-breakdown)
- [Logging](#logging)

## Docker

Docker is great because it enables cross platform software use much easier than running in terminal. 
The name of the docker image created is `weather`. 
The name of the docker container is `weather:latest`. 

### Dont know docker? 

I wont go into details but here are some commands if you dont know how to use Docker. 
Commands wrapped in `[]` are optional stuff, and `<>` are user input

| Command | explanation |
| --- | --- |
| docker ps -a | View current containers |
| docker stop <CONTAINER ID> | Stop the running container |
| docker rm <CONTAINER ID> | Remove the stopped container |
| docker-compose up [--build] [-d] weather | Spinup the server |
| docker logs <CONTAINER ID> [--follow] | View the terminal readout for the container |
| docker-compose up --build test | Run the tests for Weatherman |

---

I use `docker-compose` but regular `Docker` works just as well. 
I use four pre configured containers `weather`, `dev`, `test`, `unit-test`. 
This number will fluxuate with time but will likely reduce to only the needed ones in time. 
I intend to have a second docker-compose file for testing and a main one for the program. 

The main run command is `docker-compose up`. 
I use the different services to run the program in different ways which might be a no-no. 
Eventually I want to do it the correct way but its just much eaiser this way for now. 
`-d` creates a headless container and `--build` re-images the entire container. 

`docker-compose up [-d] [--build] [<service>]`

The main internal Docker port is `8000`. 
I have mapped `8000` for the main weather service, `8010` for development, and `8020` for testing. 

##### Dockerfile

The base is python3:latest, I set the working directory to `/usr/src/` and `COPY . .`. 
It feels like im cheating doing that but its totoly fine. 
I then set three ENV variables in the Dockerfile and one in the docker-compose which I explain later. 
I dont fully understand what the first two ENV variables do but I think it errors if they arent there. 
I commented out the update steps and things seem to run fine. It doesnt hurt anything to uncomment 
them but I was playing with things. 
I finish with running pip install on each line of the requirements.txt file. 

ENVs set:

- PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disc (equivalent to python -B option). 
- PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr (equivalent to python -u option). 
- IS_IN_DOCKER: The main.py reads this variable to determin if its in Docker or not. 
- TESTING: Used to set logging on app startup. 

The [Dockerfile](/Dockerfile)

> Note: There are still ENV variables set int he docker-compopse and I dont list out every command in the Dockerfile. 

##### docker-compose.yml

I grab version 3 because you are supposed to :man_shrugging:. 
I map the volumne to `.` so it mapps the current working directory. 
I currently expose port 8000 but that could change. 
Either way the internal port will always be 8000. 
I set some more dynamic variables depending on the container spun up. 
The weather container has `ENVIRONMENT=prod`, `TESTING=False`, and no `--reset` on uvicorn. 
For ENVIRONMENT prod is intended to be stable weather gathering. 
dev changes the name of the log file to `dev_weatherman.log`. 
For TESTING True sets all log levels to DEBUG while False sets the logfile to DEBUG and commandline to INFO. 
I plan to set the command line to INFO/WARNING enventually but for testing it works well. 
All internal ports are set to 8000 but the external ports will be `8000` or prod and `8010` for dev. 
`--reset` in uvicorn sets uvicorn to stop/start if any file in the directory updates. 
This is SUPER useful for developing but not for a stable product. 
Testing does not spin up uvicorn but instead runs behave testing or unit testing. 
These test functional and unit tests. 
Dont run these with `-d` in the docker-compose arguments because the output is important. 

Notable docker-compose.xml events:

The [docker-compose.yml](docker-compose.yml)

## SQLite

Add form and basic commands

SQL is hard to install and much easier in a container. 
There is a little/lot to SQL so i will get to it eventually. 
Its as complex as you want. 
I could set up SQL quries that do exactly what I want or i can do a general quiry then do what I want. 


## Technical breakdown

Will get to this eventually

### Crontab

Right now i have a cron set up to tell the service to get weather from the api every 15 minutres. 
Eventually this will go to every 5 and be in the system not a cron. 
I have some groundwork for an internal clock but that gets into some problems with the innerowrking 
stuff that i havnt gotten working at yet. 
One day I will and it will be great. 
Currently I have a `run.sh` script that runs a `run.py` script that hits the apps endpoints. 
Both run scripts take and pass arguments but by default poll for weather data. 
you could for instance run `run.sh -ica_report` to run the `/ica_report` endpoint. 
I added the `-ica_reports` to run every day to make sure the reports look right. 
I currenly only have the minimal arugment parsing to get the job done. 

```crontab
*/15 * * * * /<path to>/run.sh

0 0 * * * /home/acobb/git/gold_scripts/scripts/weather/run.sh -ica_report
```

In the future I intend to add a crontab to generage a weekly weather report and then email it off. 

```crontab
0 1 * * 5 /<path to>/run.sh -ica_report

0 2 * * 5 /<path to>/email_script.py
```

### Terminal

You can use uvicorn to spin up the service in terminal. 
Make sure you are in the repo and run the folowing command. 

`uvicorn main:app [--reload] --host 0.0.0.0 --port 8000`. 

## Logging

I added a lot of features to the `logger.py` class. 
The setup is a bit weird because there are two parts. 
The first one is initing the logging object with `Logger('<app_name>', [<kwargs>])`. 
The **kwargs as displayed below. 
Half the list is provided strings to use directly the other needs boolean. 
The boolean is explicit so `True/False` or `1/0`.
`'False'` is considered a string and returns `True`. 

| kwarg | What it does | input type |
| --- | --- | --- |
| `f_level`          | Update the file logging level                | string |
| `c_level`          | Update the commandline logging level         | string |
| `log_rolling`      | Set log rotating (not working yet)           | string |
| `log_directory`    | Set a logging directory (default is `logs/`) | string |
| `log_prefix`       | Set a prefix in the log file name            | string |
| `log_suffix`       | Set a suffix in the log file name            | string |
| `app_name_in_file` | Use the app name in the log file             | boolean |
| `date_in_file`     | Add the date to the log file name            | boolean |
| `time_in_file`     | Add the tiem to the log file name            | boolean |
| `utc_in_file`      | Switch the file name timestamps to utc       | boolean |
| `short_datetime`   | Shorten the dates                            | boolean |

An example of how to set up the logfile in the init phase:

```python
logger = Logger('<app_name>',\
    app_name_in_file=True,\
    date_in_file=True,\
    time_in_file=True,\
    utc_in_file=True,\
    short_datetime=True,\
    log_prefix='dev')
```

The log file will end up looking like this `logs/app_name_dev_200926-174000Z`. 
I chose to have the prefix come after the app name. 
I figured this would be easiest if there were multiple programs logging to the same directory. 

The next part of seting up logger is to set up the part that actually logs. 
This is done with something like this: `logit = logger.return_logit()`.
There are a bunch of different objects and this was the easiest way to allow me to update the 
logging class after it had been spun up. 
To log you would run something like `logit.info('<something to log>')`. 
There are three objects being used here. 
The module `logging`, the handler `logger`, and the thing that sends the logs `logit`. 
When you are updating logging its against the `logger` object and when you are logging its 
against the `logit` object (or whatever you called it). 
In the rest of the markdown I will be refering to them by those names. 
Alltogether this is how i have my logging set up:

```python
logger = logger.Logger('weatherman', app_name_in_file=True)
logit = logger.return_logit()
logit.debug('logger and logit are set up')
```

---

Because of the difference between logit and logger you can update waht the logger does at any time. 
If you need to update the log level you can run `logger.update_file_level('DEBUG')`. 
Logger expects `debug`, `info`, `warning`, `error`, `critical` (case insensitive). 
You can also update the filename at any time with `logger.update_file('<app_name>', <kwargs>)`. 
When you update the file it appends a list so set it to `None` if you want it to unset something. 
Example Use cases are updateing the logger based on env variables as I have or switch the log levels 
and file names if you receive an error and want to capture more data about it. 
Currently if behave testing is being run I update the suffix to 'test' and all log levels to debug. 
If the environment is dev or test (not prod) I add that as a suffix. 
If the script is spun up outside of docker "text" is added to the scriptname. 

---

In a nutshell weatherman logs to `logs/weatherman.log` if we are in prod, `logs/weatherman_dev.log` if 
tweaking in dev, and `logs/weatherman_dev_test.log` if running behave testing. 
