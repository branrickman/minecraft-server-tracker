from mst.settings import DATABASES_PATH

from pathlib import Path
from datetime import datetime

from peewee import *



def get_database(path: Path=Path(f"{DATABASES_PATH}/{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.db").as_posix(), *args, **kwargs):
    return SqliteDatabase(path, *args, **kwargs)



if __name__ == "__main__":
    get_database()
