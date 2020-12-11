# Weatherman

Historic weather data is surprisingly hard to come by. 
Thus the Weather man was born. 
(His hero backstory is ***REALLY*** lame). 
What you need to know is it would be nice to have a way to save weather data and recall it later. 

Weatherman collects data every x number of minutes and saves it to a sql database. 
(Currently I use a crontab but I want to switch to an internal timer of some sort). 
The data is returned in two notable ways. 
Either a dump which will return all data that meets the search parameters or a report which will shorten the data and give you an overview of each storm at the location. 

> Release:  1.3.0

> Last modified:  2020-12-11

## Table of contents

- [How to use](#how-to-use)
- [More details](#more-details)
- [Contact me](#contact-me)

## How to use

For first time setup follow [Setup](docs/backend.md#setup). 

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
3. Start the container
    - If you are using Linux or MacOS run `./spinup_server.sh`.
    - If you are in Windows run `spinup_server_for_windows.bat`.
    - Headless (Linux/MacOS only) `./build setup reset-all` for setup and `./build run` to spin up the container.
    - Note: When you try to grab city locations for the first time it can take a while because the server needs to download a large file and parse it. 
4. Once your container is up you can connect to it with any webgui by going to `localhost:8000`
    - Go to Setup at the top right of the window or the app will direct you if you try to go to a location and it has not been set up yet. 

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
    - [Setup](docs/backend.md#setup)
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
    - [TODO](https://github.com/aecobb53/weatherman/issues)
    - [Links](docs/catchall.md#links)
    - [Resources](docs/catchall.md#resources)

## Contact me

Hey! Thanks for reading this far, currently this is still a major work in progress. 
For things with the program you can submit issues but if you need to reach out to me directly 
you can at <aecobb53@gmail.com>. 
Please no spam, I almost didnt put any contact information on here. 
