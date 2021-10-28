from pathlib import Path


ROOT_PATH = Path(__file__).parent.absolute()
"""Root path of this repository."""
DATA_PATH = Path(ROOT_PATH, 'data')
"""The path to data folder."""

DATABASE_PATH = Path(DATA_PATH, 'databases')
"""The path where all databases will be stored."""
DATABASE_DATETIME_FILE_FORMAT = r"%m-%Y"
"""The datetime format for database files. New databases are created every 1 month."""
