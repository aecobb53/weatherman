

Feature: SQL butler

@database
Scenario: Creating a sql database
Does the database set up and accept perfect data?

    Given I create an empty database
    When I load the weather data in good_weather_data.json
    When I try to write the data to the database
    When I try to get all data from the database
    When I try to select element(s) 0 from the database return
    Then I verify the database response matches good_weather_data.json

@database @DEBUG
Scenario: Adding multiple weather reports to database
Does the database take a list of weather and return the list?

    Given I create an empty database
    Given I start with a new url from example_weather_api_private.json and example_urls.json
    When I load the example response data in good_owma_response.json
    When I try to write the data to the database
    When I try to get all data from the database
    When I try to select element(s) 0,1,2,3 from the database return
    Then I verify the database response matches good_multiple_weather_data.json

@database
Scenario: Tuple to dict
Does the tupe to dict function work properly?

    Given I create an empty database
    When I try to set up a tuple from good_raw_database.json
    Then I verify the interpreted data matches good_raw_database_check.json

@database
Scenario: List of tuples to list of dicts
Does the list tuple to list dict function work properly?

    Given I create an empty database
    When I try to set up a list from good_raw_database.json
    Then I verify the interpreted data matches good_raw_database_check.json

@database
Scenario: Use parameters to return results from the database
Does the database take a list of weather and return the list?

    Given I create an empty database
    Given I start with a new url from example_weather_api_private.json and example_urls.json
    When I load the example response data in good_owma_response.json
    When I try to write the data to the database

    When I set up a parameters search
    When I add exact_list=602
    When I add exact_list=601
    When I use the parameters to get data from the database
    Then I verify the database response matches good_parameter_data.json


# gets all data
# gets bad data
# gets first and last data


