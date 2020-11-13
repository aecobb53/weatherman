# Weatherman

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




  
