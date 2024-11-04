## TODO

- Existing TODO comments
- Am I logging correctly in instakarma-admin?
- Extract common code
- Handle exceptions that I throw
- Find and fix all IntelliJ warnings
- Add comments to all classes and methods
- Write README
  - Include env vars needed
- Make manual test script/plan and store it in this repo
- Add Rosie, Melissa, Jean as test users to sandbox
- Run everything through Claude for suggestions
- Delete unused Exceptions
- Should any methods be static? Is there any advantage to that?
- Run IntelliJ's code checker and fix any problems


## Object-oriented rewrite

Entity: class
  name: str
  user_id: str
  opt_in: bool
  karma: int
  add()
  ~get_status()~
  change_status()
  get_top_granters()
  get_top_recipients()
  list_entities(mode) [static?]

Karma: class
  granter: name
  recipient: name
  amount: int
  grant()

Utilities: module
  list_entities()
  get_entities() (by karma or alpha)



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
