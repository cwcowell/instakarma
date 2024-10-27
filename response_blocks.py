"""Slack text blocks used to respond to various instakarma slash commands and operations."""

disable_me: list[dict] = [
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": ">You're now disabled in instakarma\n" +
                    ">Re-enable with */instakarma enable-me*"
        }
    }
]

enable_me: list[dict] = [
    {
        "type": "section",
        "text":
            {
                "type": "mrkdwn",
                "text": ">You're now enabled in instakarma\n" +
                        ">Disable with */instakarma disable-me*"
            }
    }
]

help: list[dict] = [
    {
        "type": "header",
        "text":
            {
                "type": "plain_text",
                "text": "instakarma usage",
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
                         "*/instakarma my-stats*   see your karma and top granters and receivers\n"
                         "*/instakarma disable-me*   decline to participate in instakarma\n"
                         "*/instakarma enable-me*   participate in instakarma\n"
                         "*/instakarma help*   display this usage guide\n")
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
                    "text": "Karma of entities (not people)",
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


def my_stats(name: str, your_karma_text: str, top_recipients_text: str, top_granters_text: str) -> list[dict]:
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*instakarma stats for {name}*\n" +
                         "\n" +
                         your_karma_text +
                         ">\n" +
                         top_recipients_text +
                         ">\n" +
                         top_granters_text
            }
        }
    ]


def my_stats_disabled(name: str) -> list[dict]:
    return [
        {
            "type": "section",
            "text":
                {
                    "type": "mrkdwn",
                    "text": f"*instakarma stats for {name}*\n" +
                            "\n" +
                            f">You're disabled in instakarma\n" +
                            ">Re-enable with */instakarma enable-me*"
                }
        }
    ]
