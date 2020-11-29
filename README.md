# Weatherman

Historic weather data is surprisingly hard to come by. 
Thus the Weather man was born. 
(His hero backstory is ***REALLY*** lame). 
What you need to know is it would be nice to have a way to save weather data and recall it later. 

Weatherman collects data every x number of minutes and saves it to a sql database. 
(Currently I use a crontab but I want to switch to an internal timer of some sort). 
The data is returned in two notable ways. 
Either a dump which will return all data that meets the search parameters or a report which will shorten the data and give you an overview of each storm at the location. 

> Release:  1.1.0

> Last modified:  2020-11-27

## Table of contents

- [How to use](#how-to-use)
- [More details](#more-details)
- [Contact me](#contact-me)

## How to use

This program was put together because I needed weather data but I also realized it was a great way to pull together a lof of what I have learned over the years. 
It then showed me the gaps in what I knew how to do for a program so it has been a fun experience putting it together. 

Currently it runs out of a Docker container with exposed endpoints. 
I am not a frontend developer so its pretty clunky and takes me a while. 
The data is gathered from [Open Weather Map](https://openweathermap.org) which I abbreviate to `OWM` or Open Weather Map API`OWMA` when it comes up. 

### Setup

I run it out of Linux but its possible it could be run out of macOS or Windows. 
I dont really know :man_shrugging:. 
Try it out and let me know. 

1. Install Docker. 
2. Clone this repo. 
3. Run `build setup` to create the needed directories and config files. 
    - Update the etc/key.yml with your OWMA key
    - Update the etc/weather_api_private.yml to the locations you want to get weather data from. 
    If you dont know the locations you want you can find them on their website. 
    Download the large city zip file, unzip and find it. 
4. To spin up the server you need to use `build run`. 
    - For the first time I recommend using `docker-compose up --build weather`. This way you can see the output and see errors easier. 
    - `--build` will build a new image every time. Unless the code changed this is useless. 
    - `-d` spins up the server as a headless instance. It is set to reload if it is stopped. 
    - If you need to get a readout after it was started headless run `docker logs <container id>`. 
    - If you need to follow the output run `docker logs <container id> --follow`. 
5. Now that it is spun up and working you can verify the frontend by going to `localhost:8000`. 

You will know the backend is spun up if you see these two lines
```
        Waiting for application startup.
        Application startup complete.
```

All configurations will need the repo downloaded locally, and an "openweathermap.org" API key. 
To set up a key as seen in step 3 above, modify the `etc/key.yml` file. 

```yaml
Weather_Key: <key>
```

The config is also not added to protect the locations I look at. 
To set up your locations, modify the `etc/weather_api_private.yml` file. 
The shorthand abbreviations are only used for human reference and the Data dump/reports. 
The app looks exclusively at the location ID. 

Config:

```yaml
locations:
    LOCATION_SHORTHAND: CITY-ID
```

### General frontend use

The five main buttons on the web gui are `Reports`, `Json dump`, `Realtime Weather`, `State`, `Poll data on click`. 
`Reports` will generate a JSON that gives an overview of each storm. 
For more info check out the API section. 
`Data dump` will return a list of every database entry that meets the search parameters. 
Its not recommended to use unless you need that granular of detail. 
`Real-time Weather` is not used but I hope to display the current weather indicator over a map of the world. 
Its still only a concept but I think it would be super cool if I can get it to work. 
`State` gives a breakdown of the current running instance. 
This is super useful for diagnosing some problems. 
`Poll` data on click will instantly grab data from OWM. 

## More details

There is a lot more information than this README so I added it to the other documents. 
It was mostly for myself but I figured if im writing it down for myself I might as well provide it to everybody. 

- [API](docs/api.md)
- [Frontend](docs/frontend.md)
- [Backend](docs/backend.md)
    - [Docker](docs/backend.md#docker)
    - [SQLite](docs/backend.md#sqlite)
    - [Technical breakdown](docs/backend.md#technical-breakdown)
    - [Logging](docs/backend.md#logging)
    - [Reports](docs/backend.md#reports)
- [Testing](docs/testing.md)
    - [Functional](docs/testing.md#functional)
    - [Unit](docs/testing.md#unit)
- [Open Weather Map API](docs/open_weather_map_api.md)
- [Catchall](docs/catchall.md)
    - [TODO](docs/catchall.md#todo)
    - [Links](docs/catchall.md#links)
    - [Resources](docs/catchall.md#resources)

## Contact me

Hey! Thanks for reading this far, currently this is still a major work in progress. 
For things with the program you can submit issues but if you need to reach out to me directly 
you can at <aecobb53@gmail.com>. 
Please no spam, I almost didnt put any contact information on here. 
