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