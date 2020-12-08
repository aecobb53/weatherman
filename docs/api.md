# Weatherman API

All api endpoints start with an `/api` tag in the endpoint. 
So `http://localhost:/api/state` for example. 

- [/state](#state)
- [/poll](#\/poll)
- [/dump/search](#/dump/search)
- [/report/search](#/report/search)
- [/bug](#/bug)
- [/setup](#/setup)
- [Web API](#web-api)


## /state
State returns the current state of the app. 
Currently the information is similar to this json:
```json
{
    "db_name": "db/weatherman.sql",
    "env": "prod",
    "in_docker": true,
    "log_file": "logs/weatherman.log",
    "testing": false,
    "working_directory": "/usr/src/",
    "cities":[
        {"example-city": 123456}
    ],
    "setup_needed": false,
    "fh_logging": "DEBUG",
    "ch_logging": "DEBUG"
}
```
Most of the info is more for me for testing and verifying things are working they way they should. 
Eventually i plan to make it updatable as well. 

## /poll
This grabs data from Open Weather Map when the endpoint is hit. 

## /dump/search
Dump returns a list of dict db entries for the provided parameters. 
Some parameters are bool, one is a list, and two are strings. 
If the argument is a bool, it defaults to False so you only need to add it if its True. 
Each True bool adds all possible exact numbers to the exact_list so there is no need to use both. 
If you have exact numbers, exact_list is useful. 
The exact list will take lists `100,101,105`, ranges `100-106` or both `100-102,105`. 
Start and end times require `YYYY-MM-DD` but have more flexability as shown below. 

API Arguments:
| Argument              | type  |
| ---                   | ---   |
| thunderstorm=`bool`   | Bool  |
| drizzle=`bool`        | Bool  |
| rain=`bool`           | Bool  |
| snow=`bool`           | Bool  |
| atmosphere=`bool`     | Bool  |
| clouds=`bool`         | Bool  |
| clear=`bool`          | Bool  |
| exact_list=`string`   | string  |
| start_time=`string`   | time  |
| end_time=`string`     | time  |

Exact numbers:
| Argument      | Sky keys |
| ---           | --- |
| thunderstorm  | All 2## sky_key's |
| drizzle       | All 3## sky_key's |
| rain          | All 5## sky_key's |
| snow          | All 6## sky_key's |
| atmosphere    | All 7## sky_key's |
| clouds        | All 8## sky_key's |
| clear         | The 800 sky_key   |

Time formats:
| Time Format               |
| ---                       |
| `%Y-%m-%dT%H:%M:%S.%f`    |
| `%Y-%m-%dT%H:%M:%S`       |
| `%Y-%m-%dT%H:%M`          |
| `%Y-%m-%dT%H`             |
| `%Y-%m-%d`                |

The results will be returned as a json:
```json
[
    {
        "name": "example site", 
        "sky": "Snow", 
        "sky_id": 600, 
        "sky_desc": "light snow", 
        "temp": 8.6, 
        "wind": 20.8, 
        "time": "2020-01-01T00:00:00"
    }
]
```

## /report/search
Report returns a dict of dict db entries for the provided parameters. 
Note the parameters are mostly the same as the dump ones. 
Some parameters are bool, one is a list, and two are strings. 
If the argument is a bool, it defaults to False so you only need to add it if its True. 
Each True bool adds all possible exact numbers to the exact_list so there is no need to use both. 
If you have exact numbers, exact_list is useful. 
The exact list will take lists `100,101,105`, ranges `100-106` or both `100-102,105`. 
Start and end times require `YYYY-MM-DD` but have more flexability as shown below. 

API Arguments:
| Argument              | type  |
| ---                   | ---   |
| thunderstorm=`bool`   | Bool  |
| drizzle=`bool`        | Bool  |
| rain=`bool`           | Bool  |
| snow=`bool`           | Bool  |
| atmosphere=`bool`     | Bool  |
| clouds=`bool`         | Bool  |
| clear=`bool`          | Bool  |
| exact_list=`string`   | string  |
| start_time=`string`   | time  |
| end_time=`string`     | time  |

Exact numbers:
| Argument      | Sky keys |
| ---           | --- |
| thunderstorm  | All 2## sky_key's |
| drizzle       | All 3## sky_key's |
| rain          | All 5## sky_key's |
| snow          | All 6## sky_key's |
| atmosphere    | All 7## sky_key's |
| clouds        | All 8## sky_key's |
| clear         | The 800 sky_key   |

Time formats:
| Time Format               |
| ---                       |
| `%Y-%m-%dT%H:%M:%S.%f`    |
| `%Y-%m-%dT%H:%M:%S`       |
| `%Y-%m-%dT%H:%M`          |
| `%Y-%m-%dT%H`             |
| `%Y-%m-%d`                |

The results will be returned as a json. 
The json will have a key for each city in the config and a list of all storms returned. 
Each element of the storms list is another list with details of the storm. 
The first and last elements of the list are the start and end of the storm. 
If there are any changes to the storm they are added. 
In the example below the storm starts with a sky_id code of 620 but 20 hours later the storm changes to 600. 
It stays that code until 04:00 the next day. 
Because the example would have been too long but there was value in showing where the seccond storm would be I added a string instead of more data. 

```json
{
    "city name":[
        [
            {
                "name": "city name", 
                "sky": "Snow", 
                "sky_id": 620, 
                "sky_desc": "light shower snow", 
                "temp": 28.4, 
                "wind": 3.36, 
                "time": "2020-01-01T00:00:00"
            },
            {
                "name": "city namepb", 
                "sky": "Snow", 
                "sky_id": 600, 
                "sky_desc": "light snow", 
                "temp": 30.2, 
                "wind": 5.82, 
                "time": "2020-01-01T20:00:00"
            },
            {
                "name": "city name", 
                "sky": "Snow", 
                "sky_id": 600, 
                "sky_desc": "light snow", 
                "temp": 28.4, 
                "wind": 5.82, 
                "time": "2020-01-02T04:00:00"
            }
        ],
        [
            "storm 2 would go here"
        ]
    ]
}
```

## /bug
_still being built_

## /setup
Its possible to set up the app in one API call if you know all the values you need. 
If you dont you can perform calls and get responses. 

The list of arguments and their datatypes or exact values are below:
| argument      | datatype              | default                   |
| ---           | ---                   | ---                       |
| `action`      | `refresh`/`submit`    | `refresh`                 |
| `key`         | string                | default key placeholder   |
| `delete`      | list                  | `[]`                      |
| `newname`     | list                  | `[]`                      |
| `city`        | list                  | `[]`                      |
| `citySearch`  | string                | `None`                    |
| `cityId`      | string                | `None`                    |
| `stateAbbr`   | string                | `None`                    |
| `countryAbbr` | string                | `None`                    |
| `lat`         | string                | `None`                    |
| `lon`         | string                | `None`                    |

By default `action` is set to refresh. 
If you override it with `submit` it will update the config files and save all changes. 
`key` updates the Open Weather Map API key value. 
`delete`, `newname`, and `city` are used to udpate the list of locations. 
By using `city`, `citySearch`, `cityId`, `stateAbbr`, `countryAbbr`, `lat`, and `lon` you can set up searches on the available locations for Open Weather Map. 

For an example of setting up the locations list lets try to add some locations. 
I add `{"CitySearch":"Denver"}` to the arguments to return any city who has _Denver_ in their name. 
I look through the results and want to use `Denver City` and `Denver County`. 
I will add `{"city":["Denver=5520110", "DenverCounty=5419396"]}` to the arguments. 
If I refresh I will see them in the list of locations. 
These two locations have different names but if i grabbed locations that share the same name I would see "*" appear after the city name. 
To delete an element of the list provide the city id as seen here `{"delete":"5419396"}`. 
The biggest difference between the web gui and the API is the rename ability. 
I have been unable to add it to the API so I reccomend selecting the name of the city when you pick the city. 
On the web GUI i reccommend adding the city and then renamming it. 


## Web API


You can reach the service from any web gui by going to 

```http
http://0.0.0.0:8000/

or

0.0.0.0:8000

or

localhost:8000
```
