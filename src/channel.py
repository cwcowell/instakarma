from dataclasses import dataclass

@dataclass(frozen=True)
class Channel:
    """Info about a single Slack channel."""
    id: str
    name: str
