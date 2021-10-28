from mst.settings import DATABASE_PATH, DATABASE_DATETIME_FILE_FORMAT

from pathlib import Path
from datetime import datetime

from peewee import *



def get_database(database_name: Path=Path(f"{datetime.now().strftime(DATABASE_DATETIME_FILE_FORMAT)}.db"), directory_path: Path=DATABASE_PATH, *args, **kwargs):
    return SqliteDatabase(Path(directory_path, database_name), *args, **kwargs)



if __name__ == "__main__":
    get_database().connect()
