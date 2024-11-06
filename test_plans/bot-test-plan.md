## db initialization

**db-init**
Given there is no DB
When instabase-bot starts
Then it creates an empty DB
PASS

## karma to person

**grant to valid user**
Given @alice is in DB
And @bob is in DB
When @alice `@bob++`
Then adds row to 'grants' table
And updates @bob in 'entities' table
And logs grant
And messages Slack
PASS

Given @alice is not in DB
And @bob is in DB
When @alice `@bob++`
Then adds row to 'grants' table
And adds @alice to 'entities' table
And updates @bob in 'entities' table
And logs grant
And message to Slack
PASS

Given @alice is in DB
And @bob is not in DB
When @alice `@bob++`
Then adds row to 'grants' table
And adds @bob to 'entities' table
And logs grant
And messages Slack
PASS

Given @alice is not in DB
And @bob is not in DB
When @alice `@bob++`
Then adds row to 'grants' table
And adds @alice to 'entities' table
And adds @bob to 'entities' table
And logs grant
And messages Slack
PASS

## karma to object

Given @alice is in DB
And foo is in DB
When @alice `foo++`
Then adds row to 'grants' table
And updates foo in 'entities' table
And logs grant
And messages Slack
PASS

Given @alice is not in DB
And foo is in DB
When @alice `foo++`
Then adds row to 'grants' table
And adds @alice to 'entities' table
And updates foo in 'entities' table
And logs grant
And messages Slack
PASS

Given @alice is not in DB
And foo is not in DB
When @alice `foo++`
Then adds row to 'grants' table
And adds @alice to 'entities' table
And adds foo to 'entities' table
And logs grant
And messages Slack
PASS


## karma to invalid user

Given @alice is in DB
And @bar is an invalid user
When @alice `@bar++`
Then logs attempt
And messages Slack
PASS

Given @alice is not in DB
And @bar is an invalid user
When @alice `@bar++`
Then logs attempt
And messages Slack
PASS

## negative karma

When `foo--`
Then foo loses 1 karma
And grant is logged
And messages Slack
PASS

When `@bob--`
Then messages Slack saying not allowed
And attempt is logged
PASS

# granter is opted out

Given @alice is opted out
When @alice `@bob++`
Then logs attempt
And messages Slack
PASS

Given @alice is opted out
When @alice `foo++`
Then logs attempt
And messages Slack
PASS


# recipient is opted out

Given @bob is opted out
When @alice `@bob++`
Then logs attempt
And messages Slack
PASS

Given foo is opted out
When @alice `foo++`
Then logs attempt
And messages Slack
PASS


## self-karma
When @alice `@alice++`
Then logs attempt
And messages Slack
PASS

Given @alice is opted-out
When @alice `@alice++`
Then logs attempt
And messages Slack
PASS

## /instakarma opt-out/opt-in

Given @bob is opted in
When @bob `/instakarma opt-out`
Then logs status change
And updates @bob in 'entities' table
And messages Slack
PASS

Given @bob is opted in
When @bob `/instakarma opt-in`
Then logs status change attempt
And messages Slack
PASS

Given @bob is opted out
When @bob `/instakarma opt-in`
Then logs status change
And updates @bob in 'entities' table
And messages Slack
PASS

Given @bob is opted out
When @bob `/instakarma opt-out`
Then logs status change attempt
And messages Slack
PASS

## /instakarma leaderboard

Given there are lots of entities with positive and negative karma
And @alice is opted-in
When @alice `/instakarma leaderboard`
Then logs leaderboard request
And messages Slack with all objects and karma in descending karma order
And message excludes any people
PASS

Given there are lots of entities with positive and negative karma
And @alice is opted-out
When @alice `/instakarma leaderboard`
Then logs leaderboard request
And messages Slack with all objects and karma in descending karma order
And message excludes people
PASS

Given there are entities with the same karma
When @alice `/instakarma leaderboard`
Then logs leaderboard request
And messages Slack with all objects and karma in descending karma order
And tied entries are alphabetical order
PASS

Given there are no entities in DB
When @alice `/instakarma leaderboard`
Then logs leaderboard request
And messages Slack with header but no values
And message excludes people
PASS

## /instakarma my-stats

Given @alice has karma from multiple users
And @alice has granted karma to multiple users
When @alice `/instakarma my-stats`
Then messages Slack with her karma
And message shows top 5 recipients
And message shows top 5 granters
PASS

Given @zoe is not in the DB
When @zoe `/instakarma my-stats`
Then messages Slack with 0 karma, 0 granters, 0 recipients
PASS

Given @alice is opted-out
And @alice has karma from multiple users
And @alice has granted karma to multiple users
When @alice `/instakarma my-stats`
Then messages slack saying stats not available
And message includes opt-in instructions
PASS

## /instakarma help

When @alice `/instakarma help`
Then Bot displays all available commands
PASS

Given @alice is opted-out
When @alice `/instakarma help`
Then Bot displays all available commands
PASS


## Edge Cases

Given Database is temporarily non-writable
When alice `bob++`
Then messages slack to try again later

When @alice `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa++`
Then user is added to DB with karma
PASS

When @alice `foo++--++`
Then foo gets 1 karma
PASS
