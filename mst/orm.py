"""
    The models are divided into 2 main categories:
    - Normal models
    - Record models

    **Normal** models hold data that is constant and never changes, such as server address or player username.
    Although you can change this data, from the perspective of this scrapper, it is permanent.

    **Record** models hold data that can change over time, such as server version (server can update to a new version), server MOTD/description
    (can be changed in server properties), player count, etc.
"""

import typing as t

from mst.settings import DATABASE_PATH

from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

from peewee import *



@dataclass
class Server:
    host: t.Optional[str] = None
    port: int = 25565
    source: str = None



class BaseModel(Model):
    id: int



class DB_Server(BaseModel):
    """
        - `hostname` - Server hostname/IP address
        - `port` - Server port

        ### Backrefs:
        - `records` - All record for this server
    """

    host = CharField()
    port = IntegerField(default=25565)
    records: t.Iterable['DB_ServerRecord']


    @property
    def ip_address(self) -> str:
        return f"{self.host}:{self.port}"



    class Meta:
        db_table = 'servers'



class DB_Record(BaseModel):
    """
        - `timestamp` - The timestamp of the record
    """

    timestamp = DateTimeField(default=datetime.now)



class DB_ServerRecord(DB_Record):
    """
        - `source` - From what webpage was this server scrapped
        - `latency` - Server latency (in ms)
        - `version` - Server version
        - `is_modded` - Is the server modded?
        - `description` - Server MOTD/description
        - `max_players` - Max players online
        - `online_players_number` - Players online (number)
        - `server` - Server that this record belongs to

        ### Backrefs:
        - `online_players` - Players online (list)
    """

    source = CharField(null=True)
    latency = FloatField(null=True)
    version = CharField(null=True)
    is_modded = BooleanField(default=False)
    description = TextField(null=True)
    max_players = IntegerField()
    online_players_number = IntegerField(default=0)
    server = ForeignKeyField(DB_Server, backref='records', null=True, unique=True)
    rs_players: t.Iterable['DB_PlayerRecordsRelationship']


    def get_players(self) -> t.Iterator['DB_Player']:
        query = (DB_Player.select().join(DB_PlayerRecordsRelationship, on=DB_PlayerRecordsRelationship.player).where(DB_PlayerRecordsRelationship.record == self.id))

        return query


    class Meta:
        db_table = 'server_records'



class DB_Player(BaseModel):
    """
        - `uuid` - UUID
        - `username` - Username
        - `server_record` - `ServerRecord` where this player was last seen at
    """

    uuid = CharField(max_length=36)
    username = CharField(max_length=16)
    rs_server_records: t.Iterable['DB_PlayerRecordsRelationship']



    def seen_at(self, server: DB_Server) -> t.Optional[int]:
        return DB_PlayerRecordsRelationship.select().where(DB_PlayerRecordsRelationship.player == self).join(DB_ServerRecord, on=DB_PlayerRecordsRelationship.record).where(DB_ServerRecord.server == server).count()



    class Meta:
        db_table = 'players'



class DB_PlayerRecordsRelationship(BaseModel):
    player = ForeignKeyField(DB_Player, backref='rs_server_records')
    record = ForeignKeyField(DB_ServerRecord, backref='rs_players')

    
    class Meta:
        db_table = 'rs_player_server_records'




ALL_MODELS: t.List[t.Type[Model]] = [DB_Server, DB_ServerRecord, DB_Player, DB_PlayerRecordsRelationship]


def initialize_database(database_name: Path=Path(f"database.db"), directory_path: Path=DATABASE_PATH, *args, **kwargs) -> SqliteDatabase:
    database = SqliteDatabase(Path(directory_path, database_name), *args, **kwargs)
    database.bind(ALL_MODELS)
    database.create_tables(ALL_MODELS)

    return database


DATABASE = initialize_database()
