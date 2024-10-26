## TODO

- Review logger.debug and logger.info to make sure I'm using the right levels for different messages
[x] Break out the respond text into a separate file
- Consider merging log.py back into instakarma-bot
- Extract common code
- Handle exceptions that I throw
- Find and fix all IntelliJ warnings

## Plan for parsing and managing recipients

### Recognized user

Message contains granter's `user_id` and recipient's `user_id`.
We need granter's `name` and recipient's `name` for logging.

* For user_id in [granter_user_id, recipient_user_id] 
   * If row exists in DB with that `user_id` and `name`, RETURN `name`.
   * Else if row exists for that `user_id`, look up `name` in the API and update the row with `name`. RETURN `name`.
   * Else look up the `name` in the API and insert a row with `name` and `user_id`. RETURN `name`.
* Log grant with granter's `name` and recipient's `name`.
* Say, using recipient's `name`.


### Invalid user

Message contains granter's `user_id` and invalid recipient's `name`. 
We need granter's `name` for logging.

* If row exists in DB with granter's `user_id` and `name`, RETURN `name`.
* Else if row exists for that `user_id`, look up `name` in the API and update the row with `name`. RETURN `name`.
* Else look up the `name` in the API and insert a row with `name` and `user_id`. RETURN `name`.
* Log grant with granter's `name` and invalid recipient's `name`.
* Say, using invalid recipient's `name`.


### Object

Message contains granter's `user_id` and recipient's `name`.
We need granter's `name` for logging.

* If row exists in DB with granter's `user_id` and `name`, RETURN `name`.
* Else if row exists for that `user_id`, look up `name` in the API and update the row with `name`. RETURN `name`.
* Else look up the `name` in the API and insert a row with `name` and `user_id`. RETURN `name`.
* Log grant with granter's `name` and recipient's `name`.
* Say, using recipient's `name`.
