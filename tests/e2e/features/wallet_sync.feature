Feature: DOGECICS Wallet Synchronization
  As a CICS user
  I want to sync my Dogecoin wallet with the mainframe
  So that I can view and manage my cryptocurrency from CICS

  Background:
    Given the DOGECICS system is running
    And a Dogecoin wallet is configured

  Scenario: First time wallet synchronization
    Given no previous sync has occurred
    When I run the sync command
    Then a VSAM file should be created
    And the VSAM file should contain balance records
    And the VSAM file should contain pending balance
    And the VSAM file should contain a control record

  Scenario: Viewing wallet balance
    Given the wallet has been synced
    When I check the balance
    Then I should see the available balance
    And I should see the pending balance
    And the balance should be formatted correctly

  Scenario: Viewing transaction history
    Given the wallet has transactions
    When I request the transaction list
    Then I should see all transactions
    And each transaction should have a timestamp
    And each transaction should have an address
    And each transaction should have an amount

  Scenario: Incremental sync with new transactions
    Given the wallet has been synced previously
    And new transactions have occurred
    When I run the sync command again
    Then only new transactions should be uploaded
    And the VSAM file should be updated
    And the control record should be maintained

  Scenario: Handling large transaction volumes
    Given the wallet has more than 7648 transactions
    When I run the sync command
    Then the system should limit to 7648 records
    And the most recent transactions should be included
    And balance records should always be present
    And the control record should be maintained

  Scenario: Sending Dogecoin from CICS
    Given I have sufficient balance
    When I submit a send request with a valid address and amount
    Then the transaction should be queued
    And the transaction should be processed
    And the wallet should be updated

  Scenario: Error handling for invalid send
    Given I have insufficient balance
    When I submit a send request for more than my balance
    Then the system should reject the transaction
    And an error message should be displayed

  Scenario: System recovery after connection loss
    Given a sync was in progress
    When the connection is lost
    Then the system should handle the error gracefully
    And data integrity should be maintained
