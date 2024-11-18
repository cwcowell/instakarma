from logging import Logger
from string_mgr import StringMgr

from slack_bolt import App
from slack_sdk.errors import SlackApiError
from slack_sdk.web import SlackResponse


class SlackApiMgr:
    def __init__(self, app: App, logger: Logger):
        self.app = app
        self.logger = logger

    def get_name_from_slack_api(self, user_id: str) -> str:
        """ Use Slack API to convert a user ID like 'U07R69E3YKB' into a name like '@elvis'. """
        try:
            user_info: SlackResponse = self.app.client.users_info(user=user_id)
        except SlackApiError as sae:
            self.logger.error(StringMgr.get_string('slack-api.error', response=sae.response))
            raise
        name: str = user_info['user']['name']
        return '@' + name
