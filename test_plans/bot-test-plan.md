## db initialization

Given there is no DB
When instabase-bot starts
Then it creates an empty DB


## karma to person

Given @alice is in DB
And @bob is in DB
When @alice `@bob++`
Then adds row to 'grants' table
And updates @bob in 'entities' table
And logs grant
And messages Slack

Given @alice is not in DB
And @bob is in DB
When @alice `@bob++`
Then adds row to 'grants' table
And adds @alice to 'entities' table
And updates @bob in 'entities' table
And logs grant
And message to Slack

Given @alice is in DB
And @bob is not in DB
When @alice `@bob++`
Then adds row to 'grants' table
And adds @bob to 'entities' table
And logs grant
And messages Slack

Given @alice is not in DB
And @bob is not in DB
When @alice `@bob++`
Then adds row to 'grants' table
And adds @alice to 'entities' table
And adds @bob to 'entities' table
And logs grant
And messages Slack


## karma to object

Given @alice is in DB
And foo is in DB
When @alice `foo++`
Then adds row to 'grants' table
And updates foo in 'entities' table
And logs grant
And messages Slack

Given @alice is not in DB
And foo is in DB
When @alice `foo++`
Then adds row to 'grants' table
And adds @alice to 'entities' table
And updates foo in 'entities' table
And logs grant
And messages Slack

Given @alice is not in DB
And foo is not in DB
When @alice `foo++`
Then adds row to 'grants' table
And adds @alice to 'entities' table
And adds foo to 'entities' table
And logs grant
And messages Slack


## negative karma

When `foo--`
Then foo loses 1 karma

When `@bob--`
Then messages Slack saying not allowed
And attempt is logged


# granter is opted out

Given @alice is opted out
When @alice `@bob++`
Then logs attempt
And messages Slack

Given @alice is opted out
When @alice `foo++`
Then logs attempt
And messages Slack


# recipient is opted out

Given @bob is opted out
When @alice `@bob++`
Then logs attempt
And messages Slack

Given foo is opted out
When @alice `foo++`
Then logs attempt
And messages Slack



## self-karma
When @alice `@alice++`
Then logs attempt
And messages Slack

Given @alice is opted-out
When @alice `@alice++`
Then logs attempt
And messages Slack


## /instakarma opt-out/opt-in

Given @bob is opted in
When @bob `/instakarma opt-out`
Then logs status change
And updates @bob in 'entities' table
And messages Slack

Given @bob is opted in
When @bob `/instakarma opt-in`
Then logs status change attempt
And messages Slack

Given @bob is opted out
When @bob `/instakarma opt-in`
Then logs status change
And updates @bob in 'entities' table
And messages Slack

Given @bob is opted out
When @bob `/instakarma opt-out`
Then logs status change attempt
And messages Slack


## /instakarma leaderboard

Given there are lots of entities with positive and negative karma
And @alice is opted-in
When @alice `/instakarma leaderboard`
Then logs leaderboard request
And messages Slack with all objects and karma in descending karma order
And message excludes any people

Given there are lots of entities with positive and negative karma
And @alice is opted-out
When @alice `/instakarma leaderboard`
Then logs leaderboard request
And messages Slack with all objects and karma in descending karma order
And message excludes people

Given there are no entities in DB
When @alice `/instakarma leaderboard`
Then logs leaderboard request
And messages Slack with headers but no values
And message excludes people

Given there are entities with the same karma
When @alice `/instakarma leaderboard`
Then logs leaderboard request
And messages Slack with all objects and karma in descending karma order
And tied entries are alphabetical order


## /instakarma my-stats

Given @alice has karma from multiple users
And @alice has granted karma to multiple users
When @alice `/instakarma my-stats`
Then messages Slack with her karma
And message shows top 5 recipients
And message shows top 5 granters

Given @zoe is not in the DB
When @zoe `/instakarma my-stats`
Then messages Slack with 0 karma, 0 granters, 0 recipients

Given @alice is opted-out
And @alice has karma from multiple users
And @alice has granted karma to multiple users
When @alice `/instakarma my-stats`
Then messages slack saying stats not available
And message includes opt-in instructions


## /instakarma help

When @alice `/instakarma help`
Then Bot displays all available commands

Given @alice is opted-out
When @alice `/instakarma help`
Then Bot displays all available commands


## Edge Cases

Given Object's name has special characters "foo!@#$%^&*()_+-=[]{}\|;':",./<>?"
When @alice `foo!@#$%^&*()_+-=[]{}\|;':",./<>?++`
Then Karma is granted correctly

Given Database is temporarily non-writable
When User attempts to grant karma
Then Bot handles the error gracefully
And Informs user to try again

When @alice `aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa++`
Then user is added to DB with karma

When @alice `foo++--++`
Then foo gets 1 karma
