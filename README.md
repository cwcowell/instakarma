# Instakarma: a karmabot for Instabase

Instakarma is a Slack app that lets Instabase users thank people and complain about things.

It's written in Python using Slack's [slack_bolt SDK](https://tools.slack.dev/bolt-python/).

There are 2 runnable Python programs:

* `instakarma-bot` is the karma bot's main logic
* `instakarma-admin` is an administration tool that mostly provides an easy way to make common SQL calls to help maintain or edit instakarma's DB


## Architecture

Instakarma requires a Slack app with certain permissions to be installed in a Slack workspace. See the **Running instakarma-bot** section below for details.

It also requires the `instakarma-bot` program to be running on a server somewhere. This program creates a websocket connection to either the Slack app or the Slack workspace (I'm not sure which, but it doesn't matter). All messages in public channels, private channels, or multi-person DMs in that Slack workspace are sent via websocket to `instakarma-bot`, which listens for karma-related text (like `foo++` or `/instakarma my-stats`) and acts on any karma-related text it sees. For example, if `instakarma-bot` sees `foo++` in a message, it updates the DB to grant karma to the entity `foo`.

The `instakarma-admin` program is an optional administration tool. It never needs to be run, but can be a helpful way to manage the instakarma DB, export data, etc.


## Features of `instakarma-bot`

* Grant karma to a coworker: `@robin++` or `@robin ++`
* Grant karma to anything or anyone that's not a coworker: `foo++` or `foo ++`
* Remove karma from anything or anyone that's not a coworker: `foo--` or `foo --`
* Get help: `/instakarma help`
* See karma of anything or anyone who isn't a coworker: `/instakarma leaderboard`
* See your own stats: `/instakarma my-stats`
    * How much karma you have
    * Who or what you've given the most karma to
    * Who or what you've removed the most karma from
    * Who has given you the most karma
* Opt yourself in to Instakarma: `/instakarma opt-in` (this is the default state)
* Opt yourself out of Instakarma: `/instakarma opt-out`


## Features of `instakarma-admin`

* Add a coworker, non-coworker person, or thing to the instakarma DB: `./instakama-admin add-entity foo`. _This is not normally needed, as entities are added automatically the first time they grant or receive karma._
* Back up the DB to a local file: `./instakarma-admin backup-db`
* Export a list of all karma grants to a CSV file for auditing: `./instakarma-admin export-grants`
* List all entities by descending karma: `./instakarma-admin list-by-karma`
* List all entities by name: `./instakarma-admin list-by-name`
* List all entities who are opted out: `./instakarma-admin list-opted-out`
* Opt an entity in: `./instakarma-admin opt-in @foo`
* Opt an entity out: `./instakarma-admin opt-out @foo`


## Running `instakarma-bot`

You need to make a Slack app, install it to your Slack workspace, and run `instakarma-bot` on some server (or your laptop). 

When you run `instakarma-bot` it will listen for any karma-related messages on whatever Slack workspace the app is installed to and handle karma or **/instakarma** commands as appropriate.

Here's how to get things set up.

1. Make a slack app with these tokens or configuration settings:
    * An app-level token with `connections:write` scope
    * A bot token with these **OAuth Scopes**:
        * `channels:history`
        * `chat:write`
        * `commands`
        * `groups:history`
        * `im:history`
        * `mpim:history`
        * `users:read`
    * A user token with these **OAuth Scopes**: (_not sure if this is necessary?_)
        * `identity.basic`
    * **Event Subscriptions** enabled
    * **Interactivity & Shortcuts** enabled
    * **Slash Commands** enabled
    * **Socket mode** enabled
    * These **Event Subscriptions**:
        * `message.channels`
        * `message.groups`
        * `message.mpim`
1. Set env vars
   * `export SLACK_APP_TOKEN=<SLACK-APP-TOKEN-THAT-STARTS-WITH-'xapp-'>`
   * `export SLACK_BOT_TOKEN=<SLACK-BOT-TOKEN-THAT-STARTS-WITH-'xoxb-'>`
1. Make sure Python 3.12+ is installed (it might work on earlier versions, but was only tested on 3.12 and 3.13)
1. `cd <REPO-ROOT-DIR>`
1. `pip install -r requirements.txt` (you only have to do this once)
1. `cd src`
1. `./instakarma-bot`


## Running `instakarma-admin`

1. Make sure Python 3.12+ is installed (it might work on earlier versions, but was only tested on 3.12 and 3.13)
1. `cd <REPO-ROOT-DIR>`
1. `pip install -r requirements.txt` (you only have to do this once)
1. `cd src`
1. `./instakarma-admin help`


## Contributing

Anyone at Instabase is welcome to refactor or improve existing instakarma code. 

Check with the contributors below before adding new features, since we want to keep it easy to maintain and HR-approved.


### Prerequisites

* Python 3.12+ -- it might work on earlier versions, but was only tested on 3.12 and 3.13
* `pip install -r requirements.txt` -- to install Python dependencies
* A free [Slack API sandbox](https://api.slack.com/docs/developer-sandbox) -- for testing
* A Slack app configured as described in the section above -- for testing


### FAQ

* I launched the bot with `./instakarma-bot`, so why does nothing happen when I type `foo++` in a Slack channel? _Check `logs/instakarma.log` for errors. If there are no errors, did you invite the instakarma to the channel or DM you typed `foo++` in? If not, invite it by mentioning `@instakarma` in that channel or DM._
* Where does instakarma work? _Public channels, private channels, and multiple-person DMs. It doesn't work in 1-to-1 DMs._
* Is this spyware? _The `instakarma-bot` program uses regexes to look for certain phrases (like `++`) in text typed by users, but it doesn't store or forward any of the text it sees. It isn't spyware._


### Contributors

Chris Cowell - `christopher.cowell@instabase.com` or `christopher.w.cowell@gmail.com`


### License

Copyright © 2024 Christopher W. Cowell <br/>
All rights reserved.