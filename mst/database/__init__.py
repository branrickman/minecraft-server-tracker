from pathlib import Path
from datetime import datetime

from playhouse.sqlite_ext import *



# TODO:
def get_database(path: Path=Path(ROOT_PATH, 'database', f"{datetime.strftime('%x-%X')}.db"), *args, **kwargs):
    return SqliteExtDatabase(path)
