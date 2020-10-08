

Feature: SQL butler

@database
Scenario: Creating a sql database
Does the database set up and accept perfect data?

    Given I create an empty sql_database
    When I load the weather data in good_weather_data.json
    When I try to write the data to the database
    When I try to get all data from the database
    When I try to select element(s) 0 from the database return
    Then I verify the database response matches good_weather_data.json

@database
Scenario: Adding multiple weather reports to database
Does the database take a list of weather and return the list?

    Given I create an empty sql_database
    Given I start with a new url from example_weather_api_private.json and example_urls.json
    When I load the example response data in good_weather_response_data.json
    When I try to write the data to the database
    When I try to get all data from the database
    # When I try to select element(s) 0 from the database return
    When I try to select element(s) 0,1,2,3,4,5,6,7,8,9,10 from the database return
    Then I verify the database response matches good_multiple_weather_data.json


# Scenario: tuple to dict
# Does the tupe to dict function work properly?


# list of tuples to dicts
# gets all data
# gets bad data
# gets first and last data


