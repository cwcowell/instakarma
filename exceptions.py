class SelfGrantError(Exception):
    """A greedy user has tried to grant themselves karma.

    This should be handled.
    """
    pass


class OptedOutEntityError(Exception):
    """A user has tried to grant karma to an opted-out entity.

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


class NoSlackApiMgrDefinedError:
    """Tried to make a Slack API call, but no mgr is defined.

    This should be handled.
    """
    pass