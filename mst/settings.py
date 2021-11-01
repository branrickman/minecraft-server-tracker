from pathlib import Path
from re import compile


ROOT_PATH = Path(__file__).parent.absolute()
"""Root path of this repository."""
DATA_PATH = Path(ROOT_PATH, 'data')
"""The path to data folder."""

DATABASE_PATH = Path(DATA_PATH, 'databases')
"""The path where all databases will be stored."""

PLAYER_USERNAME_REGEX = compile(r'^[a-zA-Z_0-9]{2,16}$')
"""
    Some plugins allow you to show text when hovering on the player list. They actually just create fake players with names in the player list.
    This RegEx checks whether each player name is valid when obtaining player list, so we don't save crap.
"""
