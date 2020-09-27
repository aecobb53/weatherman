# Weatherman Behave Testing

## Table of Contents

## Running

In Docker:

`docker-compose up --build test`

In terminal (this is fine to run wherever as long as you have `behave` installed). 
Make sure you are in the man directory `.../weather/`

`behave`


`behave` - Full behave run

`behave features/<feature file>` - Single feature run

`behave features/<feature file>:<line number of scenario>` - Single scenario in a feature. 
While it seems to be fine if the line number is anywhere in the scenario, its easiest if you try to 
get the line where the scenario starts. 

## Features

## Steps