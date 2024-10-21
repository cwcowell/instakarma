# Recognized user

Message contains granter's `user_id` and recipient's `user_id`.
1. Get granter's `name` from DB
1. If doesn't exist:
    1. Look up granter's user_name from API
    1. Add granter (with `user_id` and `name`) to DB
1. Get recipient's `name` from DB
1. If doesn't exist:
    1. Look up recipient's user_name from API
    1. Add recipient (with `user_id` and `name`) to DB
1. Log grant with granter's `name` and recipient's `name`
1. Say, using recipient's `name`


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