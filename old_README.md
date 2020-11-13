# Weatherman

<!-- Added -->

> Release:  0.6.0-beta

> Point of contact:  Andrew

> Last modified:  2020-11-13


## Table of Contents

<!-- Added -->

 - [Weatherman API](#weatherman-api)
 - [Open Weather Map API](#open-weather-map-api)
 - [Docker setup](#docker-setup)
 - [Terminal setup](#terminal-setup)
 - [SQL setup](#sql-setup)
 - [CSV setup](#csv-setup)
 - [Crontab](#crontab)
 - [Docker](#docker)
 - [Terminal](#terminal)
 - [SQL](#sql)
 - [CSV](#csv)
 - [Logging](#logging)
 - [TODO](#todo)
 - [Links](#links)

 [Behave testing README](/README_behave.md)

## Weatherman API

<!-- Skipped -->

You can reach the service from any web gui by going to 

```http
http://0.0.0.0:8000/

or

0.0.0.0:8000

or

localhost:8000
```

Going to any of the above addresses will bring you to a makeshift menu i created. 
This will give you a list of all url extentions and a brief description of what they do. 
In general 
- `/state` is for general system stuff like is it in Docker or not. 
- `/*dump` is for returning a list of dicts for all data matching the weather type.
- `/*report` returnsthe folowing nested data and creates a json report with the same data
  but formatted a bit better. 

```text
list of cities
    list of storms two elements long
        dict of first element is the start of the storm
        dict of second element is the last of the storm
```

###### `/`	            

Menu

###### `/state`	        

The state is an instance variable that keeps track of useful info such as: 

- working_directory - The directory in Docker (or terminal) being used. 
- in_docker - Boolean representing in Docker?
- env - Env is more for human understanding between prod/dev/test
- testing - Boolean representing are unit/feature tests being run?
- reports - If a report was generated where would it be placed? 
- log_file - Where is the app logging to?
- cities - A list of dicts {cities:city_id} being polled
- fh_logging - What is the file log level 
- ch_logging - What is the commandline log level 

###### `/poll`	        

Poll data from Open Weather Map based on the list of cities

###### `/full_dump`	    

"Return a list of all bad weather in db"

###### `/ica_dump`	    

"Return bad weather for ICAs"

###### `/rain_dump`	    

"Return rain data"

###### `/snow_dump`	    

"Return snow data"

###### `/wind_dump`	    

"Return wind data"

###### `/full_report`	

"File of bad data in report"

###### `/ica_report`	

"File of bad weather for ICAs"

###### `/rain_report`	

"File of rain data"

###### `/snow_report`	

"File of snow data"

###### `/wind_report`	

"File of wind data"

---


## What you need

All configurations will need the repo downloaded locally, and an "openweathermap.org" API key. 
To set up a key add the folowing to a file in the repo called `key.ignore`. 

```json
{"Weather_Key": "<key>"}
```

The config is also not added to protect the locations i look at. 
Copy the config example below. 
The shorthand abbreviations are only used for human reference. 
The app looks exclusivly at the location ID. 

Config:

```json
{
    "locations": {
        "shorthand abreviation": 00000,
    },
    "url":"https://api.openweathermap.org/data/2.5/"
}
```




  
