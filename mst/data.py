import typing as t

import asyncio
try:
    import uvloop # type: ignore
except ImportError:
    uvloop = None

from peewee import Database

from mst.orm import DATABASE, DB_Player, DB_PlayerRecordsRelationship, DB_Server, DB_ServerRecord
from mst.scrappers import Server, scrap_from_all_scrappers

import mst.pinger as pinger

_PSS = t.TypeVar('_PSS', pinger.PingedServer, Server)



def yield_servers_from_database(database: Database=DATABASE, at_once: int=25) -> t.Generator[t.List[DB_Server], None, None]:
    query = (DB_Server.select().bind(database)) # type: t.Iterator[DB_Server]
    servers: t.List[DB_Server] = []

    for server in query:
        if len(servers) < at_once:
            servers.append(server)
            continue

        yield servers
        servers.clear()



def save_into_database(server: _PSS, database: Database=DATABASE) -> _PSS:
    (DB_Server.replace(
        host=server.host,
        port=server.port
    ).execute(database))
    saved_server = DB_Server.get((DB_Server.host == server.host) & (DB_Server.port == server.port)) # type: DB_Server
    print("Saved server:", saved_server, f"({saved_server.ip_address} | {server.source})")

    if getattr(server, 'status', None):
        (DB_ServerRecord.replace(
            source=server.source,
            latency=server.status.latency,
            version=server.status.version,
            is_modded=server.status.is_modded,
            description=server.status.description,
            max_players=server.status.players.max,
            online_players_number=server.status.players.online,
            server=saved_server
        ).execute(database))
        saved_server_record = DB_ServerRecord.get(DB_ServerRecord.server == saved_server) # type: DB_ServerRecord
        print("Saved record:", saved_server_record)

        for player in server.status.players.list:
            (DB_Player.replace(
                uuid=player.uuid,
                username=player.username,
            ).execute(database))
            saved_player = DB_Player.get((DB_Player.uuid == player.uuid) & (DB_Player.username == player.username)) # type: DB_Player

            (DB_PlayerRecordsRelationship.replace(
                player=saved_player,
                record=saved_server_record
            ).execute(database))
            print("Saved player:", saved_player)




async def scrap_from_all_scrappers_and_save(*args, **kwargs):
    for servers in scrap_from_all_scrappers(*args, **kwargs):
        for server in servers:
            if server.host:
                save_into_database(server=server, database=DATABASE)



async def ping_and_update(*args, **kwargs):
    async for servers in pinger.ping_all(*args, **kwargs):
        for server in servers:
            save_into_database(server=server, database=DATABASE)



async def ping_from_all_scrappers_and_save(*args, **kwargs):
    for scrapped_servers in scrap_from_all_scrappers(*args, **kwargs):
        statuses = await asyncio.gather(*[
            pinger.get_status(scrapped_server) for scrapped_server in scrapped_servers if scrapped_server and scrapped_server.host
        ])
    
        for status in statuses:
            save_into_database(server=status, database=DATABASE)



if __name__ == "__main__":
    if uvloop:
        uvloop.install()

    asyncio.run(ping_from_all_scrappers_and_save())
