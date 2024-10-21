class SelfGrantError(Exception):
    """A greedy user has tried to grant themsleves karma.

    This should be handled.
    """
    pass


class DisabledEntityError(Exception):
    """A has tried to grant karma to a disabled entity.

    This should be handled.
    """
    pass


# class UserIdToEntityNameMappingError(Exception):
#     """The 'entities' table doesn't have a value for the 'entity_name' column in a row with a given
#     value in the 'user_id' column.
#
#     Something has gone badly wrong with user creation logic, so exit the program instead of handling.
#     """
#     pass
