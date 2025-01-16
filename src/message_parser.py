from enums import Action
from string_mgr import StringMgr

from logging import Logger
import re
from re import Pattern
from typing import Final


class MessageParser:
    BACKTICK_PAIR_REGEX: Final[Pattern] = re.compile(r'`[^`]+`')

    # Regex components
    AT_SYMBOL: Final[str] = r'@'
    AT_SYMBOL_AND_USER_ID: Final[str] = r'(@\w+)'
    EITHER_OPERATOR: Final[str] = r'(\+\+|--)'
    GREATER_THAN_SYMBOL: Final[str] = r'>'
    INCREMENT_OPERATOR: Final[str] = r'(\+\+)'
    LESS_THAN_SYMBOL: Final[str] = r'<'
    NO_EXTRA_OPERATORS: Final[str] = r'(?![-+])'
    NO_PRECEDING_AT_SYMBOL: Final[str] = r'(?<!@)'
    NO_PRECEDING_LESS_THAN_SYMBOL: Final[str] = r'(?<!<)'
    ONE_OR_MORE_NON_GREATER_THAN: Final[str] = r'([^>]+)'
    WHITESPACE_OR_NOTHING: Final[str] = r'(?!\S)'
    WORD_BOUNDARY: Final[str] = r'\b'
    WORD_WITH_NO_BACKTICK_GT_LT: Final[str] = r'([^\s`<>]+)'
    WORD_WITH_NO_BACKTICK_GT_LT_AT: Final[str] = r'([^\s`<>@]+)'
    WORD_WITH_NO_BACKTICK_OR_PLUS_OR_MINUS: Final[str] = r'([^\s`+-]+)'
    ZERO_OR_ONE_WHITESPACE: Final[str] = r'\s?'

    # Assembled regexes
    INVALID_USER_RECIPIENT_REGEX: Final[str] = (NO_PRECEDING_LESS_THAN_SYMBOL +
                                                AT_SYMBOL +
                                                WORD_WITH_NO_BACKTICK_GT_LT +  # group 0
                                                INCREMENT_OPERATOR +  # group 1
                                                NO_EXTRA_OPERATORS)

    OBJECT_RECIPIENT_REGEX: Final[str] = (NO_PRECEDING_AT_SYMBOL +
                                          WORD_BOUNDARY +
                                          WORD_WITH_NO_BACKTICK_GT_LT_AT +  # group 0
                                          WORD_BOUNDARY +
                                          EITHER_OPERATOR +  # group 1
                                          WHITESPACE_OR_NOTHING)

    VALID_USER_RECIPIENT_REGEX: Final[str] = (LESS_THAN_SYMBOL +
                                              AT_SYMBOL +
                                              WORD_WITH_NO_BACKTICK_OR_PLUS_OR_MINUS +  # group 0
                                              GREATER_THAN_SYMBOL +
                                              ZERO_OR_ONE_WHITESPACE +
                                              INCREMENT_OPERATOR +  # group 1
                                              NO_EXTRA_OPERATORS)

    print("object regex: " + OBJECT_RECIPIENT_REGEX)

    INVALID_USER_RECIPIENT_PATTERN: Final[Pattern] = re.compile(INVALID_USER_RECIPIENT_REGEX)
    OBJECT_RECIPIENT_PATTERN: Final[Pattern] = re.compile(OBJECT_RECIPIENT_REGEX)
    VALID_USER_RECIPIENT_PATTERN: Final[Pattern] = re.compile(VALID_USER_RECIPIENT_REGEX)

    def __init__(self, logger: Logger):
        self.logger = logger

    def find_backtick_pairs(self, text: str) -> list[tuple[int, int]]:
        """Find the indices of all backtick pairs in a string.

        :returns: List of tuples where each tuple contains the start and end indices of a backtick pair
        """
        backtick_pairs = []
        for match in self.BACKTICK_PAIR_REGEX.finditer(text):
            backtick_pairs.append((match.start(), match.end()))
        return backtick_pairs

    def remove_matches_within_backticks(self,
                                        matches: list[tuple[str, Action]],
                                        text: str) -> list[tuple[str, Action]]:
        """Remove matches that are within backticks from the list of matches."""
        backtick_pairs = self.find_backtick_pairs(text)
        filtered_matches: list[tuple[str, Action]] = []
        end_pos_of_last_match: int = 0
        for match in matches:
            start: int = text.find(match[0], end_pos_of_last_match)
            end: int = start + len(match[0])
            end_pos_of_last_match = end
            within_backticks: bool = False
            for pair in backtick_pairs:
                if start > pair[0] and end < pair[1]:
                    within_backticks = True
                    break
            if not within_backticks:
                filtered_matches.append(match)
        return filtered_matches

    def detect_valid_user_recipients(self, text: str) -> list[tuple[str, Action]]:
        """Capture "foo" and "++" from "<@foo>++" and "<@foo> ++".

        This covers cases where the recipient is a user registered in Slack.
        Decrementing karma from valid users is not allowed, so this method doesn't look for "--".
        Slack doesn't recognize @-mentioning usernames when within backticks, so we don't need to
        look for backticks like we do for invalid users and objects.

        :returns: List of tuples where each tuple contains a recipient's name and the Action (increment or decrement)
        """

        matches: list[tuple[str, Action]] = self.VALID_USER_RECIPIENT_PATTERN.findall(text)
        valid_user_recipients = [(user_id,
                                  Action.INCREMENT if action == Action.INCREMENT.value else Action.DECREMENT)
                                 for user_id, action in matches]
        return valid_user_recipients

    def detect_invalid_user_recipients(self, text: str) -> list[tuple[str, Action]]:
        """Capture "foo" from "@foo++" and "@foo ++" where there's no "<" before the "@".

        This covers cases of trying to grant karma to a user not registered in Slack.

        :returns: List of tuples where each tuple contains an invalid user's name and
                  the Action (increment or decrement)
        """

        matches: list[tuple[str, Action]] = self.INVALID_USER_RECIPIENT_PATTERN.findall(text)
        invalid_user_recipients: list[tuple[str, Action]] = self.remove_matches_within_backticks(matches, text)
        invalid_user_recipients = [(user_id,
                                    Action.INCREMENT if action == Action.INCREMENT.value else Action.DECREMENT)
                                   for user_id, action in invalid_user_recipients]
        return invalid_user_recipients

    def detect_object_recipients(self, text: str) -> list[tuple[str, Action]]:
        """Capture "foo" and "++" or "--' from "foo++" and "foo--" only when there's no @ before "foo".

        This covers cases where the recipient is an object, like "banyan" or "the-internet".

        :returns: List of tuples where each tuple contains an object's name and
                  the Action (increment or decrement)
        """

        matches: list[tuple[str, Action]] = self.OBJECT_RECIPIENT_PATTERN.findall(text)
        object_recipients: list[tuple[str, Action]] = self.remove_matches_within_backticks(matches, text)
        object_recipients = [(user_id.lower(),
                             Action.INCREMENT if action == Action.INCREMENT.value else Action.DECREMENT)
                             for user_id, action in object_recipients]
        return object_recipients

    def get_amount_verb_emoji(self, action: Action) -> tuple[int, str, str]:
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
