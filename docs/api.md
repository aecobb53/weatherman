how to use
what does it have
response forms and examples

## Weatherman API

You can reach the service from any web gui by going to 

```http
http://0.0.0.0:8000/

or

0.0.0.0:8000

or

localhost:8000
```

`/api/poll`

When this endpoint is hit the script grabs data from OWMA. 

`/api/state`

This returns the state of the app. 

| Key               | Shorthand                 |
| ---               | ---                       |
| db_name           | Current database          |
| env               | Env (prod, dev, test)     |
| in_docker         | Bool, in Docker           |
| log_file          | Current log file          |
| testing           | bool Running tests        |
| working_directory | Directory in container    |
| cities            | List of cities            |
| file_logging      | File logging level        |
| consol_logging    | Console logging level     |

`/api/dump` _Not working yet_

This takes kwargs and returns a list of dicts from data that matches the search. 

| Key           | Datatype      | Default value | Description |
| ---           | ---           | ---   | --- |
| thunderstorm  | Bool          | False | All 2## sky_key's |
| drizzle       | Bool          | False | All 3## sky_key's |
| rain          | Bool          | False | All 5## sky_key's |
| snow          | Bool          | False | All 6## sky_key's |
| atmosphere    | Bool          | False | All 7## sky_key's |
| clouds        | Bool          | False | All 8## sky_key's |
| clear         | Bool          | False | The 800 sky_key   |
| exact_list    | list(ints)    | None  | Exact sky_keys    |
| start_time    | datetime(str) | None  | _See below_       |
| end_time      | datetime(str) | None  | _See below_       |

`Exact_list` will take any combination of keys or ranges. 
So it will take `200, 202,350-510, 530 - 800`. 
Note the commas matter but not the spaces. 

`*_time` is looking for a datetime like this `YYYY-MM-DDTHH:MM:SSZ`. 
But will accept a space instead of the `T`, and a `L` or no character ending. 
I havnt built it out yet but i want to accept Zulu and local timestamps even though the database is saved in Zulu. 

`/api/report` _Not working yet_

Currently this is called the exact same as the `/api/dump` but it returns a differently formatted list. 
The format of the returned json. 
```text
list of cities
    list of storms
        storm_start
        storm_end
        storm_durration
        start_dct
        end_dct
        storm_events
```

The start and end dct are the first and last weather reports in the storm. 
If there are any changes in the storm or notable events they get listed out in the storm_events. 
The start and end storm are excluded from this list to prevent duplication of data. 
