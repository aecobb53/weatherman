# Weathermans catchall documentation

## Table of contents

- [TODO](#todo)
- [Links](#links)
- [Resources](#resources)

## TODO

- db structure in the readme. 
- log rotating.
- ~~Add to report the worst conditions of a storm.~~
- Condensed sql db. As in a report database for longer term trending. 
- ~~Set import versions in the requirements file~~
- Transition off a crontab
- If i have different docker-compose &| Dockerfiles change the requirements.txt file to only include the testing for tests.
- Update the readme api
- Enable dump and reportrs for specific locations.
    - temperature
    - winds
- Try to move the dump and report guts to another function so it can be called easier


### 1.0 release requirements

- [ ] Review all markdown 
- [ ] Spellcheck markdown
- [x] Figure out what happend to PB
- [ ] Add api to markdown


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


