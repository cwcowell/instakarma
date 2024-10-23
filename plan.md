# Recognized user

Message contains granter's `user_id` and recipient's `user_id`.

## Convert user_ids to names for logging
* For user_id in [granter_user_id, recipient_user_id] 
   * If row exists in DB with that `user_id` and `name`, RETURN `name`.
   * Else if row exists for that `user_id`, look up `name` in the API and update the row with `name`. RETURN `name`.
   * Else look up the `name` in the API and insert a row with `name` and `user_id`. RETURN `name`.
* Log grant with granter's `name` and recipient's `name`
* Say, using recipient's `name`


# Unrecognized user

Message contains granter's `user_id` and recipient's invalid `user_name`.

1. Get granter's `name` from DB
1. If doesn't exist:
    1. Look up granter's user_name from API
    1. Add granter (with `user_id` and `name`) to DB
1. Log invalid grant with granter's `name` and recipient's `name`
1. Say, using recipient's `name`


# Object

Message contains granter's `user_id` and recipient's `name`.

1. Get granter's `name` from DB
1. If doesn't exist:
    1. Look up granter's user_name from API
    1. Add granter (with `user_id` and `name`) to DB
1. Log grant with granter's `name` and recipient's `name`
1. Say, using recipient's `name`