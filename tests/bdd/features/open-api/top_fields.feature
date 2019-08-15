Feature: total
    Answer consist of top level fields

Scenario: Get fields
    Given I am authorised user
    # And
    When I request search
    # And
    Then I get all top level fields

