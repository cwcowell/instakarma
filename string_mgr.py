import json
from pathlib import Path
from string import Template
from typing import Final


class StringMgr:
    _STRINGS_FILE: Final[str] = 'strings.json'
    _PLACEHOLDER: Final[str] = 'PLACEHOLDER_UI_STRING'  # return this if the key isn't in the map

    _strings_map: dict[str, str] = {}
    _is_map_loaded: bool = False

    @classmethod
    def _load_map(cls):
        """ Load file with user-facing strings into a map that we can use throughout
        instakarma-bot and instakarma-admin.

        :raises FileNotFoundError: if the JSON file doesn't exist
        :raises JSONDecodeError: if the JSON file is malformed
        """
        strings_file_path: Path = Path(cls._STRINGS_FILE)
        with open(strings_file_path) as strings_file:
            cls._strings_map = json.load(strings_file)

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
        except:
            # return f"<STRING FOR {key_path!r} UNDEFINED>"
            return StringMgr.get_string("error.undefined_string", undefined_key_path=key_path)
