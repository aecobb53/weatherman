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

### Open Weather Map api

I am using the Free calls:

```
60 calls/minute
1,000,000 calls/month
Curent Weather
Minute Forecast 1 hour*
Hourly Forecast 2 days*
Daily Forecast 7 days*
Government Weather alerts*
Historical weather 5 days*
Basic weather maps
Weather triggers
Weather widgets
Uptime 95%

* - 1,000 API calls per day by using One Call API
** - 2,000 API calls per day by using One Call API
```

Note: I read somewhere the polling type i am using maxes out at 20. 
I cant find where that was again so maybe that changed. 
It appears i can call for current weather up to 60/min or 1M/month. 
If that is the case i can poll up to 22 cities every minute. 
Currently i only get 11 cities data every 15 minutes. 
I plan to increase to every 5 minutes.


| calls/attempt          | 10        | 11      | 20      | 23        |
| ----------------------:| ---------:| -------:| -------:| ---------:|
| calls/min              | 10        | 11      | 20      | 23        |
| calls/hour             | 600       | 660     | 1,200   | 1,380     |
| calls/day              | 14,400    | 15,840  | 28,800  | 33,120    |
| calls/week             | 100,800   | 110,880 | 201,600 | 231,840   |
| calls/month            | 446,400   | 491,040 | 892,800 | 1,026,720 |
| calls every 5  minutes | 89,280    | 98,208  | 178,560 | 205,344   |
| calls every 10 minutes | 44,640    | 49,104  | 89,280  | 102,672   |
| calls every 15 minutes | 29,760    | 32,736  | 59,520  | 68,448    |
| calls every 30 minutes | 14,880    | 16,368  | 29,760  | 34,224    |
| calls every 60 minutes | 7,440     | 8,184   | 14,880  | 17,112    |

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





## TODO

- better error handling. 
- verify the run scripts error silently and capture all returns so the cront does not get full. 
- logging in the readme. 
- reports in the readme. 
- db structure in the readme. 
- update Dockerfile or docker-compose itteration numbers. 
- log rotating.
- Add to report the worst conditions of a storm. 
- Date search from the database
- Condensed sql db
- Set import versions in the requirements file
- Add CICD daily testing. pull changes, run tests, send results. 
- Change all backends to be `async`
- Eventually set the main app logging to file only
- Shorten up main README and add it to an extended README
  - README - Basics of the app and where to go for more information
  - Testing - Details on testing how to perform, what to expect
  - OWA - Details about the weather service
  - Env - Docker, SQL, 
  - Frontend - html, css, if i write an actual frontend which is very tempting
  - Other - Catchall
- Transition off a crontab
- Add intervul detail to the json dump?
- lock requirements.txt versions
- mo config
- update log levels of master to the intended levels. 

## Links

- [prod api](http://0.0.0.0:8000/state)
- [dev api](http://0.0.0.0:8010/state)
- [test api](http://0.0.0.0:8020/state)


- [SQL help](https://www.sqlite.org/lang_expr.html#cosub)
- [Open Weather Map (OWM)](https://openweathermap.org)
- [Open Weather Map Api](https://openweathermap.org/current#format). 
  This is the link to the main OWM api info. 
- [OWM weather conditions](https://openweathermap.org/weather-conditions). 
  This is where the weather codes, icons, and brief descriptions are. 
- [OWM FAQ](https://openweathermap.org/faq)
- [OWM Pricing](https://openweathermap.org/price)
  
