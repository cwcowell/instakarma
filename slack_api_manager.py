from logging import Logger

from slack_bolt import App

# TODO: rename all "manager" objects to "mgr"

class SlackApiManager():

    def __init__(self, app: App, logger: Logger):
        self.app = app
        self.logger = logger

    def get_name_from_slack_api(self, user_id: str) -> str:
        """ Use Slack API to convert a user ID ('U07R69E3YKB') into a user name ('@elvis'). """
        self.logger.debug(f"Asking Slack API for name of user with user_id '{user_id}'")
        user_info = self.app.client.users_info(user=user_id)
        name = user_info['user']['name']
        self.logger.debug(f"Slack API returned name '{name}' for user_id '{user_id}'")
        return '@' + name
