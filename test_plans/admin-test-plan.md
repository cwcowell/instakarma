# Instakarma Admin Tool Test Plan

## Database Initialization Tests

### Test Case AI1: Fresh DB Initialization
Given: No instakarma.db file exists
When: `instakarma-admin <ANY-SUBCOMMAND>`
Then: Database is created
And: It prints a message saying so

### Test Case AI2: Existing DB Initialization
Given: instakarma.db already exists
When: `instakarma-admin <ANY-SUBCOMMAND>`
Then: Existing database is unchanged
And: It prints message saying no-op


## Entity Management Tests

### Test Case EM1: Add Basic User Entity
Given: Database exists
And: User "@alice" doesn't exist in the database
When: `instabase-admin add @alice`
Then: @alice is added to entities table
And: Her karma is 0
And: Her opted_in status is TRUE

### Test Case EM2: Add Basic Object Entity
Given: Database exists
And: Object "coffee" doesn't exist in the database
When: `instabase-admin add-entity coffee`
Then: "coffee" is added to entities table
And: Its user_id field is NULL
And: Its karma is 0
And: Its opted_in status is TRUE

### Test Case EM3: Duplicate Entity
Given: Entity "@bob" exists in the database
When: `instakarma-admin add-entity @bob`
Then: Prints info message
And: Existing entity is unchanged

### Test Case EM4: Invalid Entity Name
Given: Database exists
When: `instakarma-admin add-entity `
Then: Prints error message
And: No entity is added


## Opted-in/opted-out Status Management Tests

### Test Case OM1: Basic Opt-out
Given: Entity "@charlie" exists and is opted in
When: `instakarma-admin opt-out @charlie`
Then: Entity's opted_in status changes to FALSE
And: Command reports entity's status

### Test Case OM2: Basic Opt-in
Given: Entity "@dave" exists and is opted out
When: `instakarma-admin opt-in @dave`
Then: Entity's opted_in status changes to TRUE
And: Command reports entity's status

### Test Case OM3: Nonexistent Object Entity Status Change
Given: Entity "nonexistent" doesn't exist in DB
When: `instakarma opt-out nonexistent`
Then: Prints info message
And: No changes are made to database

### Test Case OM4: Nonexistent User Entity Status Change
Given: Entity "@zoe" doesn't exist in DB
When: `instakarma opt-out @zoe`
Then: Prints info message
And: No changes are made to database

### Test Case OM5: Redundant Status Change for Object Entity
Given: Entity "@emma" exists in DB and is already opted out
When: `instakarma opt-out @emma`
Then: Command reports that status is unchanged
And: opted_in status remains FALSE

### Test Case OM5: Redundant Status Change for User Entity
Given: Entity "@emma" exists in DB and is already opted in
When: `instakarma opt-in @emma`
Then: Command reports that status is unchanged
And: opted_in status remains TRUE


## Data Export Tests

### Test Case DE1: Basic Export
Given: Database contains multiple grants
When: `instabase-admin export-grants`
Then: CSV file is created
And: File contains all grants

### Test Case DE2: Empty Grants Export
Given: Database contains no grants
When: `instabase-admin export-grants`
Then: CSV file is created
And: File contains only headers
And: Command reports that no grants were found

### Test Case DE3: export file not writable
Given: Export file exists and is not writable
When: `instabase-admin export-grants`
Then: Command reports file not writable
And: Export file is unchanged


## Object Listing Tests

### Test Case OL1: List by Karma (Descending)
Given: Multiple objects and users exist with different karma values
When: `instakarma-admin list-by-karma`
Then: Objects are displayed in karma order (highest first)
And: Only non-user entities are shown
And: Karma values are included in output

### Test Case OL2: List Alphabetically
Given: Multiple objects and users exist
When: `instakarma-admin list-by-name`
Then: Objects are displayed in alphabetical order
And: Only non-user entities are shown
And: Karma values are included in output

### Test Case OL3: Empty Object List by karma
Given: No object entities exist in database
When: `instakarma-admin list-by-karma`
Then: Command reports no objects found
And: Empty list is displayed

### Test Case OL4: Empty Object List by name
Given: No object entities exist in database
When: `instakarma-admin list-by-name`
Then: Command reports no objects found
And: Empty list is displayed

### Test Case OL5: Objects with Same Karma
Given: Multiple objects have the same karma value
When: `instakarma-admin list-by-karma`
Then: Objects with same karma are sub-sorted alphabetically


## Database Backup Tests

### Test Case DB1: Basic Backup
Given: Valid instakarma.db exists
When: `instakarma-admin backup-db`
Then: Exact copy of database is created
And: Original database remains unchanged
And: Command reports success

### Test Case DB2: Backup with Existing Target
Given: Target backup file already exists
When: `instakarma-admin backup-db`
Then: Command reports failure and why
And: No change to backup

### Test Case DB3: Backup file not writable
Given: Target backup file already exists and is not writable
When: `instakarma-admin backup-db`
Then: Command reports failure and why
And: No change to backup


## Edge Cases

### Test Case EC1: Special Characters
Given: Database exists
When: When: `instabase-admin add foo!@#$%^&*(){}[]1;'\|,./<>?`
Then: Entity is added correctly
And: Special characters are preserved
