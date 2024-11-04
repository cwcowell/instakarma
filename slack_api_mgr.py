from logging import Logger

from slack_bolt import App
from slack_sdk.web import SlackResponse


class SlackApiMgr:

    def __init__(self, app: App, logger: Logger):
        self.app = app
        self.logger = logger

    def get_name_from_slack_api(self, user_id: str) -> str:
        """ Use Slack API to convert a user ID like 'U07R69E3YKB' into a name like '@elvis'. """
        self.logger.debug(f"Asking Slack API for name of user with user_id {user_id!r}")
        user_info: SlackResponse = self.app.client.users_info(user=user_id)
        name: str = user_info['user']['name']
        self.logger.debug(f"Slack API returned name {name!r} for user_id {user_id!r}")
        return '@' + name
