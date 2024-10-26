class SelfGrantError(Exception):
    """A greedy user has tried to grant themselves karma.

    This should be handled.
    """
    pass


class DisabledEntityError(Exception):
    """A user has tried to grant karma to a disabled entity.

    This should be handled.
    """
    pass


class UserIdNotInDbError:
    """Tried to look up a user by 'user_id' in 'entities' table, but wasn't found.
    
    This should be handled.
    """
    pass

class NameNotFoundInSlackError:
    """Tried to look up a user by `name` in Slack, but wasn't found.

    This should be handled.
    """
    pass
