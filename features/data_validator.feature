

Feature: Data validator

@validator
Scenario Outline: Exact_list
Does the validator handle the exact list types appropriatly?

    Given I set up a new datetime validator
    When I run <data> through the exact list validator
    Then I verify the exact match data matches <result>

    Examples: Datetime validator
        | data              | result                            |
        | 500               | 500                               |
        | 500,501           | 500,501                           |
        | 500 , 501         | 500,501                           |
        | 500-505           | 500,501,502,503,504               |
        | 500 - 505         | 500,501,502,503,504               |
        | 500-505,300,301   | 500,501,502,503,504,300,301       |
        | 500-505,300-306   | 500,501,502,503,504,300,301,305   |

@validator
Scenario Outline: Datetime validator
Does the validator handle the datetime strings appropriatly?

    Given I set up a new datetime validator
    When I run <data> through the datetime validator
    Then I verify the datetime data matches <result>

    Examples: Datetime validator
        | data                          | result                |
        | 2020-01-01T00:00:00.000000Z   | 2020-01-01T00:00:00Z  |
        | 2020-01-01T00:00:00.000000L   | 2020-01-01T00:00:00Z  |
        | 2020-01-01T00:00:00.000000    | 2020-01-01T00:00:00Z  |
        | 2020-01-01T00:00:00.000Z      | 2020-01-01T00:00:00Z  |
        | 2020-01-01T00:00:00.000L      | 2020-01-01T00:00:00Z  |
        | 2020-01-01T00:00:00.000       | 2020-01-01T00:00:00Z  |
        | 2020-01-01T00:00:00Z          | 2020-01-01T00:00:00Z  |
        | 2020-01-01T00:00:00L          | 2020-01-01T00:00:00Z  |
        | 2020-01-01T00:00:00           | 2020-01-01T00:00:00Z  |
        | 2020-01-01T00:00Z             | 2020-01-01T00:00:00Z  |
        | 2020-01-01T00:00L             | 2020-01-01T00:00:00Z  |
        | 2020-01-01T00:00              | 2020-01-01T00:00:00Z  |
        | 2020-01-01T00Z                | 2020-01-01T00:00:00Z  |
        | 2020-01-01T00L                | 2020-01-01T00:00:00Z  |
        | 2020-01-01T00                 | 2020-01-01T00:00:00Z  |
        | 2020-01-01                    | 2020-01-01T00:00:00Z  |
