from pathlib import Path


ROOT_PATH = Path(__file__).parent.absolute()
DATA_PATH = Path(ROOT_PATH, 'data')

DATABASES_PATH = Path(DATA_PATH, 'databases')
DATABASE_FILE_FORMAT = r"%d-%m-%Y_%H:%M:%S"
