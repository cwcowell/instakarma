from enums import Action

from logging import Logger
import re

class MessageParser:

    def __init__(self, logger: Logger):
        self.logger = logger

    def detect_valid_user_recipients(self, text: str) -> list[tuple[str, Action]]:
        """Capture "foo" and "++" from "<@foo>++" and "<@foo> ++".

        This covers cases where the recipient is a user registered in Slack.
        """
        recipient_is_valid_user_regex: str = r'<@(.*?)>\s?((\+\+)|(--))'
        regex_matches = re.findall(recipient_is_valid_user_regex, text)
        valid_user_recipients: list[tuple[str, Action]] = []
        for match in regex_matches:
            recipient_user_id: str = match[0]
            action: Action = Action.INCREMENT if match[1] == Action.INCREMENT.value else Action.DECREMENT
            valid_user_recipients.append((recipient_user_id, action))
        self.logger.debug(f"Detected valid user recipients: {valid_user_recipients}")
        return valid_user_recipients


    def detect_invalid_user_recipients(self, text: str) -> list[tuple[str, Action]]:
        """Capture "foo" from "@foo++" and "@foo ++" where there's no "<" before the "@".

        This covers cases of trying to grant karma to a user not registered in Slack.
        """
        recipient_is_invalid_user_regex: str = r'(?<!<)(@\w+)\s?(\+\+|--)'
        regex_matches = re.findall(recipient_is_invalid_user_regex, text)
        invalid_user_recipients: list[tuple[str, Action]] = []
        for match in regex_matches:
            recipient_name: str = match[0]
            action: Action = Action.INCREMENT if match[1] == Action.INCREMENT.value else Action.DECREMENT
            invalid_user_recipients.append((recipient_name, action))
        self.logger.debug(f"Detected invalid user recipients: {invalid_user_recipients}")
        return invalid_user_recipients


    def detect_object_recipients(self, text: str) -> list[tuple[str, Action]]:
        """Capture "foo" and "++" from "foo++" and "foo ++ only when there's no @ before "foo".

        This covers cases where the recipient is an object, like "banyan" or "the-internet".
        """
        recipient_is_object_regex: str = r'\b(?<!@)([\w-]+)\s?((\+\+)|(--))'
        regex_matches = re.findall(recipient_is_object_regex, text)
        object_recipients: list[tuple[str, Action]] = []
        for match in regex_matches:
            recipient_name: str = match[0].lower()
            action: Action = Action.INCREMENT if match[1] == Action.INCREMENT.value else Action.DECREMENT
            object_recipients.append((recipient_name, action))
        self.logger.debug(f"Detected object recipients: {object_recipients}")
        return object_recipients

    def get_amount_verb_emoji(self, action) -> tuple[int, str, str]:
        """ Convert an action into three elements of a Slack message: karma amount, verb, and emoji.

        :returns: Tuple with the karma amount, verb, and emoji
        """
        if action == Action.INCREMENT:
            self.logger.debug("setting amount to 1, verb to 'leveled up'")
            return 1, 'leveled up', ':arrow_up:'
        if action == Action.DECREMENT:
            self.logger.debug("setting amount to -1, verb to 'took a hit'")
            return -1, 'took a hit', ':arrow_down:'
        self.logger.critical(f"Unrecognized action is neither Action.INCREMENT nor Action.DECREMENT: {action!r}")
        return 0, 'unrecognized', ':question:'
