from enums import Action
from string_mgr import StringMgr

from logging import Logger
import re
from re import Pattern
from typing import Final


class MessageParser:
    INVALID_USER_RECIPIENT_REGEX: Final[Pattern] = re.compile(r'(?<!<)(@\w+)\s?(\+\+|--)')
    OBJECT_RECIPIENT_REGEX: Final[Pattern] = re.compile(r"\b(?<!@)([\w'-]+)\s?(\+\+|--)")
    VALID_USER_RECIPIENT_REGEX: Final[Pattern] = re.compile(r'<@(.*?)>\s?(\+\+|--)')

    def __init__(self, logger: Logger):
        self.logger = logger

    def detect_valid_user_recipients(self, text: str) -> list[tuple[str, Action]]:
        """Capture "foo" and "++" from "<@foo>++" and "<@foo> ++".

        This covers cases where the recipient is a user registered in Slack.
        """
        matches: list[tuple[str, Action]] = self.VALID_USER_RECIPIENT_REGEX.findall(text)
        valid_user_recipients = [(user_id,
                                  Action.INCREMENT if action == Action.INCREMENT.value else Action.DECREMENT)
                                 for user_id, action in matches]
        return valid_user_recipients

    def detect_invalid_user_recipients(self, text: str) -> list[tuple[str, Action]]:
        """Capture "foo" from "@foo++" and "@foo ++" where there's no "<" before the "@".

        This covers cases of trying to grant karma to a user not registered in Slack.
        """
        matches: list[tuple[str, Action]] = self.INVALID_USER_RECIPIENT_REGEX.findall(text)
        invalid_user_recipients = [(user_id,
                                    Action.INCREMENT if action == Action.INCREMENT.value else Action.DECREMENT)
                                   for user_id, action in matches]
        return invalid_user_recipients

    def detect_object_recipients(self, text: str) -> list[tuple[str, Action]]:
        """Capture "foo" and "++" from "foo++" and "foo ++ only when there's no @ before "foo".

        This covers cases where the recipient is an object, like "banyan" or "the-internet".
        """
        matches: list[tuple[str, Action]] = self.OBJECT_RECIPIENT_REGEX.findall(text)
        object_recipients = [(user_id.lower(),
                              Action.INCREMENT if action == Action.INCREMENT.value else Action.DECREMENT)
                             for user_id, action in matches]
        return object_recipients

    def get_amount_verb_emoji(self, action) -> tuple[int, str, str]:
        """ Convert an action into three elements of a Slack message: karma amount, verb, and emoji.

        :returns: Tuple with the karma amount, verb, and emoji
        """
        match action:
            case Action.INCREMENT:
                return (1,
                        StringMgr.get_string('message-parser.increment.verb'),
                        StringMgr.get_string('message-parser.increment.emoji'))
            case Action.DECREMENT:
                return (-1,
                        StringMgr.get_string('message-parser.decrement.verb'),
                        StringMgr.get_string('message-parser.decrement.emoji'))

            case _:
                self.logger.critical(StringMgr.get_string('message-parser.unrecognized.log-msg', action=action))
                return (0,
                        StringMgr.get_string('message-parser.unrecognized.verb'),
                        StringMgr.get_string('message-parser.unrecognized.emoji'))
