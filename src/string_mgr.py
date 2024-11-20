from constants import STRINGS_FILE

from pathlib import Path
import yaml


class StringMgr:
    """Converts keys to user-facing strings, so we can collect all user-facing strings in one file."""

    _strings_map: dict[str, str] = {}
    _is_map_loaded: bool = False

    @classmethod
    def _load_map(cls):
        """Load the file with user-facing strings into a map that we can use throughout instakarma-bot.

        :raises FileNotFoundError: if the JSON file doesn't exist
        :raises JSONDecodeError: if the JSON file is malformed
        """
        strings_file_path: Path = Path(STRINGS_FILE)
        with open(strings_file_path) as strings_file:
            cls._strings_map = yaml.safe_load(strings_file)
            cls._is_map_loaded = True

    @classmethod
    def get_string(cls, key_path: str, **kwargs) -> str:
        if not cls._is_map_loaded:
            cls._load_map()

        template = cls._strings_map
        try:
            for key in key_path.split('.'):
                template = template[key]
            string: str = template.format(**kwargs)
            return string
        except (AttributeError, KeyError, TypeError):
            return StringMgr.get_string("error.undefined-string", undefined_key_path=key_path)
        except yaml.YAMLError:
            return StringMgr.get_string("error.malformed-yaml", undefined_key_path=key_path)
