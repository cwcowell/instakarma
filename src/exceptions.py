"""Collect all instakarma-related exceptions in one place.

All of these custom exceptions should be handled, not ignored.
"""

class OptedOutRecipientError(Exception):
    """A user has tried to grant karma to an opted-out entity."""

    pass


class OptedOutGranterError(Exception):
    """An opted-out user has tried to grant karma."""

    pass
