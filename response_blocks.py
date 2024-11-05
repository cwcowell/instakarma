""" Slack text blocks used to respond to instakarma slash commands and instakarma operations """

from enums import Status

def change_status(new_status: Status) -> list[dict]:
    """ Generate Slack text blocks with info about a user's opted-in/opted-out status. """
    text: str = f"You're now {new_status.value} in instakarma\n"
    if new_status == Status.OPTED_OUT:
        text += "Opt in with */instakarma opt-in*"
    else:
        text += "Opt out with */instakarma opt-out*"

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
                "text": "How do I use instakarma?",
            }
    },
    {
        "type": "section",
        "text":
            {
                "type": "mrkdwn",
                "text": ("*@robin++*   give 1 karma to Slack user *@robin*\n"
                         "*python++*   give 1 karma to object *python*\n"
                         "*python--*   remove 1 karma from object *python*\n"
                         "_optionally add a space between *recipient* and *++* or *--*_\n"
                         "\n"
                         "*/instakarma help*   display this usage guide\n"
                         "*/instakarma leaderboard*   see the karma of all objects\n"
                         "*/instakarma my-stats*   see your karma and top granters and receivers\n"
                         "*/instakarma opt-in*   participate in instakarma\n"
                         "*/instakarma opt-out*   decline to participate in instakarma\n"
                         "\n"
                         "_contact christopher.cowell@instabase.com or @chris.cowell with problems_")
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
                    "text": "How much karma do objects have?",
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
                    "text": f"Instakarma stats for {name}",
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
