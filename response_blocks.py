from enums import Status


"""Slack text blocks used to respond to various instakarma slash commands and operations."""

def change_status(new_status: Status) -> list[dict]:
    text: str = f"You're now {new_status.value} in instakarma\n"
    if new_status == Status.DISABLED:
        text += "Re-enable with */instakarma enable-me*"
    else:
        text += "Disable with */instakarma disable-me*"

    return [
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": text
        }
    }
]

help: list[dict] = [
    {
        "type": "header",
        "text":
            {
                "type": "plain_text",
                "text": "Instakarma usage",
            }
    },
    {
        "type": "section",
        "text":
            {
                "type": "mrkdwn",
                "text": ("*@robin++*   give 1 karma to Slack user *@robin*\n"
                         "*python++*   give 1 karma to non-person *python*\n"
                         "*python--*   remove 1 karma from non-person *python*\n"
                         "_optionally add a space between *recipient* and *++* or *--*_\n"
                         "\n"
                         "*/instakarma disable-me*   decline to participate in instakarma\n"
                         "*/instakarma enable-me*   participate in instakarma\n"
                         "*/instakarma help*   display this usage guide\n"
                         "*/instakarma leaderboard*   see the karma for all non-person entities\n"
                         "*/instakarma my-stats*   see your karma and top granters and receivers\n")
            }
    }
]


def leaderboard(leader_text: str) -> list[dict]:
    return [
        {
            "type": "header",
            "text":
                {
                    "type": "plain_text",
                    "text": "Karma of non-person entities",
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
                "text":  your_karma_text +
                         "\n" +
                         top_recipients_text +
                         "\n" +
                         top_granters_text
            }
        }
    ]
