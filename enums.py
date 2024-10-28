from enum import Enum


class Action(Enum):
    """ Every attempt to grant karma must have an Action associated with it,
    so we know if the grant increases or decreases the recipient's karma. """
    INCREMENT = '++'
    DECREMENT = '--'


class Status(Enum):
    """ Slack users can opt out if they don't want to participate in instakarma. """
    OPT_IN: str = 'opted-in'
    OPT_OUT: str = 'opted-out'
