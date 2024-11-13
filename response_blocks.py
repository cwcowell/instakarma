""" Slack text blocks used to respond to instakarma slash commands and instakarma operations """

from enums import Status
from string_mgr import StringMgr


def change_status(new_status: Status) -> list[dict]:
    """ Generate Slack text blocks with info about a user's opted-in/opted-out status. """
    text: str = StringMgr.get_string('response-blocks.change-status.current-status', status=new_status.value) + \
                '\n'
    if new_status == Status.OPTED_OUT:
        text += StringMgr.get_string('response-blocks.change-status.opt-in-instructions')
    else:
        text += StringMgr.get_string('response-blocks.change-status.opt-out-instructions')

    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text
            }
        }
    ]


# Slack text blocks with usage info for instakarma slash commands and operations.
help: list[dict] = [
    {
        "type": "header",
        "text":
            {
                "type": "plain_text",
                "text": StringMgr.get_string('response-blocks.help.header')
            }
    },
    {
        "type": "section",
        "text":
            {
                "type": "mrkdwn",
                "text": StringMgr.get_string('response-blocks.help.section')
            }
    }
]


def leaderboard(leader_text: str) -> list[dict]:
    """ Generate Slack text blocks that contain all object names and karma. """
    return [
        {
            "type": "header",
            "text":
                {
                    "type": "plain_text",
                    "text": StringMgr.get_string('response-blocks.leaderboard.header'),
                }
        },
        {
            "type": "section",
            "text":
                {
                    "type": "mrkdwn",
                    "text": leader_text
                }
        }
    ]


def my_stats(name: str,
             your_karma_text: str,
             top_recipients_text: str,
             top_granters_text: str) -> list[dict]:
    """ Generate Slack text blocks that contain a user's karma stats. """
    return [
        {
            "type": "header",
            "text":
                {
                    "type": "plain_text",
                    "text": StringMgr.get_string('response-blocks.my-stats.header', name=name)
                }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": your_karma_text +
                        "\n" +
                        top_recipients_text +
                        "\n" +
                        top_granters_text
            }
        }
    ]
