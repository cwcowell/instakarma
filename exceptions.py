class OptedOutRecipientError(Exception):
    """A user has tried to grant karma to an opted-out entity.

    This should be handled.
    """
    pass


class OptedOutGranterError(Exception):
    """An opted-out user has tried to grant karma.

    This should be handled.
    """
    pass


class NoSlackApiMgrDefinedError:
    """Tried to make a Slack API call, but no mgr is defined.

    This should be handled.
    """
    pass
