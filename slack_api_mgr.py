from logging import Logger
from typing import Final

from slack_bolt import App
from slack_sdk.errors import SlackApiError
from slack_sdk.web import SlackResponse


class SlackApiMgr:

    def __init__(self, app: App, logger: Logger):
        self.app = app
        self.logger = logger

    def get_name_from_slack_api(self, user_id: str) -> str:
        """ Use Slack API to convert a user ID like 'U07R69E3YKB' into a name like '@elvis'. """
        self.logger.debug(f"asking Slack API for name of user with user_id {user_id!r}")
        try:
            user_info: SlackResponse = self.app.client.users_info(user=user_id)
        except SlackApiError as sae:
            self.logger.error(f"Slack API call failed: {sae.response}")
            raise
        name: str = user_info['user']['name']
        self.logger.debug(f"Slack API returned name {name!r} for user_id {user_id!r}")
        return '@' + name
