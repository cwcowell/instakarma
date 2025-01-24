from logging import Logger

from constants import CHANNEL_NAMES_TO_IGNORE
from string_mgr import StringMgr

import slack_bolt
from slack_bolt import App
from slack_sdk.errors import SlackApiError
from slack_sdk.web import SlackResponse


class SlackApiMgr:
    """Handle calls to the Slack API."""

    def __init__(self, app: App, logger: Logger):
        self.app = app
        self.logger = logger

    def get_name_from_slack_api(self, user_id: str) -> str:
        """Use Slack API to convert a user ID like 'U07R69E3YKB' into a name like '@elvis'.

        :raises SlackApiError: If something goes wrong with the API call
        """

        try:
            user_info: SlackResponse = self.app.client.users_info(user=user_id)
        except SlackApiError as sae:
            self.logger.error(StringMgr.get_string('slack-api.error', response=sae.response))
            raise
        name: str = user_info['user']['name']
        return '@' + name


    def gather_ignored_channel_ids(self, app: slack_bolt.App) -> list[str]:
        """Fetch the channel IDs for the channels that instakarma should ignore.

        :returns list[str]: The channel IDs for the channels to ignore
        """
        channel_ids_to_ignore: list[str] = []
        api_response: SlackResponse = app.client.conversations_list()
        if not api_response['ok']:
            raise SystemExit(f"Error fetching channel list from Slack: {api_response}")

        channel_map: dict[str, str] = {ch['name']: ch['id'] for ch in api_response['channels']}
        channel_ids: [str] = []
        for name in CHANNEL_NAMES_TO_IGNORE:
            if name in channel_map:
                channel_ids.append(channel_map[name])
            else:
                self.logger.info(f"Couldn't find channel ID for channel name {name!r}, so won't ignore it")
        return channel_ids
