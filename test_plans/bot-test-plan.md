# Instakarma Manual Test Plan

## Database Initialization Tests

### Test Case DB1: Fresh Installation
Given: The instakarma.db file does not exist
When: The Slack bot starts up
Then: The database file is created with the correct schema
And: The tables 'entities' and 'grants' are created with the correct columns

### Test Case DB2: Database Connection
Given: The instakarma.db file exists but is empty
When: The Slack bot starts up
Then: The bot connects successfully
And: No errors are reported

## Karma Granting Tests

### Test Case KG1: Basic Positive Karma to User
Given: User @alice exists in the database
And: User @bob exists in the database
And: Both users have opted in
When: @bob sends message "@alice++"
Then: @alice's karma increases by 1
And: A grant record is created with granter=@bob, recipient=@alice, amount=1

### Test Case KG2: First-time Granter
Given: User @alice exists in the database
And: User @charlie does not exist in the database
When: @charlie sends message "@alice++"
Then: @charlie is automatically added to the entities table
And: @alice's karma increases by 1
And: A grant record is created with granter=@charlie, recipient=@alice, amount=1

### Test Case KG3: First-time Recipient (User)
Given: User @bob exists in the database
And: User @dave does not exist in the database
When: @bob sends message "@dave++"
Then: @dave is automatically added to the entities table
And: @dave's karma increases by 1
And: A grant record is created with granter=@bob, recipient=@dave, amount=1

### Test Case KG4: Basic Positive Karma to Object
Given: Object "coffee" exists in the database
When: @alice sends message "coffee++"
Then: "coffee" karma increases by 1
And: A grant record is created with granter=@alice, recipient=coffee, amount=1

### Test Case KG5: First-time Object
Given: Object "tea" does not exist in the database
When: @bob sends message "tea++"
Then: "tea" is added to the entities table
And: "tea" karma increases to 1
And: A grant record is created with granter=@bob, recipient=tea, amount=1

### Test Case KG6: Basic Negative Karma to Object
Given: Object "meetings" exists in the database with karma=5
When: @alice sends message "meetings--"
Then: "meetings" karma decreases by 1
And: A grant record is created with granter=@alice, recipient=meetings, amount=-1

### Test Case KG7: Self Karma
Given: User @alice exists in the database
When: @alice sends message "@alice++"
Then: No karma change occurs
And: Bot responds with an error message about self-karma

### Test Case KG8: Opted-out Recipient
Given: User @bob exists in the database
And: @bob has opted out
When: @alice sends message "@bob++"
Then: No karma change occurs
And: Bot responds with a message that @bob has opted out

### Test Case KG9: Opted-out Granter
Given: User @alice has opted out
When: @alice sends message "@bob++"
Then: No karma change occurs
And: Bot responds with a message that opted-out users cannot grant karma

## Opt-in/Opt-out Tests

### Test Case OO1: Basic Opt-out
Given: User @alice exists in the database
And: @alice has opted in
When: @alice sends "/instakarma opt-out"
Then: @alice's opted_in status is set to FALSE
And: Bot confirms the opt-out

### Test Case OO2: Basic Opt-in
Given: User @bob exists in the database
And: @bob has opted out
When: @bob sends "/instakarma opt-in"
Then: @bob's opted_in status is set to TRUE
And: Bot confirms the opt-in

### Test Case OO3: Redundant Opt-out
Given: User @alice exists in the database
And: @alice has already opted out
When: @alice sends "/instakarma opt-out"
Then: Bot responds that @alice is already opted out
And: No database change occurs

### Test Case OO4: First-time User Opt-out
Given: User @dave does not exist in the database
When: @dave sends "/instakarma opt-out"
Then: @dave is added to the entities table
And: @dave's opted_in status is set to FALSE
And: Bot confirms the opt-out

## Leaderboard Tests

### Test Case LB1: Basic Leaderboard
Given: Multiple objects exist with different karma scores
When: @alice sends "/instakarma leaderboard"
Then: Bot displays objects sorted by karma in descending order
And: No user entities are shown in the leaderboard

### Test Case LB2: Empty Leaderboard
Given: No object entities exist in the database
When: @bob sends "/instakarma leaderboard"
Then: Bot responds that no objects have received karma yet

### Test Case LB3: Tied Scores
Given: Objects "coffee" and "tea" both have 5 karma
When: @alice sends "/instakarma leaderboard"
Then: Both objects are shown with the same karma score
And: Their relative order is consistent (e.g., alphabetical)

## My Stats Tests

### Test Case MS1: Basic Stats View
Given: User @alice has karma history
And: @alice has granted and received karma from multiple users
When: @alice sends "/instakarma my-stats"
Then: Bot shows @alice's current karma
And: Shows top 5 recipients of @alice's karma
And: Shows top 5 granters of karma to @alice

### Test Case MS2: New User Stats
Given: User @dave is new to the system
When: @dave sends "/instakarma my-stats"
Then: Bot shows 0 karma
And: Shows empty lists for top recipients and granters
And: Includes a helpful message about how to start using karma

### Test Case MS3: Opted-out User Stats
Given: User @bob has opted out
When: @bob sends "/instakarma my-stats"
Then: Bot shows stats are unavailable while opted out
And: Includes instructions how to opt back in

## Help Tests

### Test Case H1: Basic Help
Given: Any user state
When: User sends "/instakarma help"
Then: Bot displays all available commands
And: Shows example usage for each command

## Edge Cases

### Test Case EC1: Special Characters in Names
Given: Object contains special characters "my-project#1"
When: User sends "my-project#1++"
Then: Karma is granted correctly
And: Object name is stored with special characters intact

### Test Case EC2: Concurrent Karma Grants
Given: Multiple users attempt to grant karma simultaneously
When: @alice and @bob both send "@charlie++" at the same time
Then: Both grants are recorded correctly
And: @charlie's karma increases by 2

### Test Case EC3: Database Lock
Given: Database is temporarily locked
When: User attempts to grant karma
Then: Bot handles the error gracefully
And: Informs user to try again

### Test Case EC4: Long Names
Given: Object name is very long (>100 characters)
When: User attempts to grant karma to the object
Then: Bot handles the long name appropriately
And: Either truncates with notification or returns an error

### Test Case EC5: Rate Limiting
Given: User @alice sends many karma grants rapidly
When: Rate limit is exceeded
Then: Bot responds with rate limit message
And: Ignores excess karma grants

### Test Case EC6: Multiple Karma Operators
Given: Message contains "coffee++--++"
When: @alice sends the message
Then: Only the first operator is processed
And: "coffee" receives +1 karma
