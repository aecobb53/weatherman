# Open Weather Map api

I am using the Free calls:

```
60 calls/minute
1,000,000 calls/month
Current Weather
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

Note: I read somewhere the polling type I am using maxes out at 20. 
I cant find where that was again so maybe that changed. 
It appears i can call for current weather up to 60/min or 1M/month. 
If that is the case I can poll up to 22 cities every minute. 
Currently I only get 11 cities data every 15 minutes. 
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
