from constants import IGNORED_CHANNELS

from typing import Final

IGNORED_CHANNEL_IDS: Final[set] = {channel.id for channel in IGNORED_CHANNELS}
IGNORED_CHANNEL_MAP: Final[dict] = {channel.id: channel.name for channel in IGNORED_CHANNELS}

def ignore_channel(channel_id: str) -> bool:
    """Is a channel ID among the list of channel IDs that instakarma should ignore?"""
    return channel_id in IGNORED_CHANNEL_IDS

def ignored_channel_id_to_name(channel_id: str) -> str | None:
    """Converts a channel ID to its channel name."""
    return IGNORED_CHANNEL_MAP[channel_id]
