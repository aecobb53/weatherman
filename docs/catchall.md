# Weathermans catchall documentation

## Table of contents

- [TODO](#todo)
- [Links](#links)
- [Resources](#resources)

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
- ~~Shorten up main README and add it to an extended README~~
  - ~~README - Basics of the app and where to go for more information~~
  - ~~Testing - Details on testing how to perform, what to expect~~
  - ~~OWA - Details about the weather service~~
  - ~~Env - Docker, SQL, ~~
  - ~~Frontend - html, css, if i write an actual frontend which is very tempting~~
  - ~~Other - Catchall~~
- Transition off a crontab
- ~~Add intervul detail to the json dump?~~ no.
- lock requirements.txt versions
- mo config
- update log levels of master to the intended levels. 
- Create a setup script that grabs the list of potential locations for a user to select places. 
- Transition the jsons in etc/ to yml

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

## Resources


