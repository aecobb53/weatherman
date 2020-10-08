

Feature: Weather butler

@owma
Scenario: Generating a poll url
Does the database set up a proper url and argument setup

    Given I start with a new url from example_weather_api_private.json and example_urls.json
    When I map the url
    Then I verify the url matches example_urls.json base

@owma @off
Scenario: Successful poll
Does the responce module work and reutrn a 200 error code
It can also be used to verify their server is working with the app

    Given I start with a new url from example_weather_api_private.json and example_urls.json
    When I map the url
    Then I get a response from owma

@owma @off
Scenario: weather butler poll function
Does the poll function take the responce and return a list of dicts

    Given I start with a new url from example_weather_api_private.json and example_urls.json
    When I map the url
    When I poll owma

@owma
Scenario: data returned is formatted correctly
Does the data formatter format data properly

    Given I start with a new url from example_weather_api_private.json and example_urls.json
    When I load the example response data in good_owma_response.json

