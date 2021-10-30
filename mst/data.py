import typing as t

import asyncio
try:
    import uvloop # type: ignore
except ImportError:
    uvloop = None

from peewee import Database

from mst.database import DATABASE, Player, PlayerRecordsRelationship, Server, ServerRecord
from mst.scrappers import ScrappedServer, scrap_from_all_scrappers

import mst.pinger as pinger

_PSS = t.TypeVar('_PSS', pinger.PingedServer, ScrappedServer)



def yield_servers_from_database(database: Database=DATABASE, at_once: int=25) -> t.Generator[t.List[Server], None, None]:
    query = (Server.select().bind(database)) # type: t.Iterator[Server]
    servers: t.List[Server] = []

    for server in query:
        if len(servers) < at_once:
            servers.append(server)
            continue

        yield servers
        servers.clear()



def save_into_database(server: _PSS, database: Database=DATABASE) -> _PSS:
    (Server.replace(
        host=server.host,
        port=server.port
    ).execute(database))
    saved_server = Server.get((Server.host == server.host) & (Server.port == server.port)) # type: Server

    if getattr(server, 'status', None) is not None:
        (ServerRecord.replace(
            source=server.source,
            latency=server.status.latency,
            version=server.status.version,
            is_modded=server.status.is_modded,
            description=server.status.description,
            max_players=server.status.players.max,
            online_players_number=server.status.players.online,
            server=saved_server
        ).execute(database))
        saved_server_record = ServerRecord.get(ServerRecord.server == saved_server) # type: ServerRecord

        for player in server.status.players.list:
            (Player.replace(
                uuid=player.uuid,
                username=player.username,
            ).execute(database))
            saved_player = Player.get((Player.uuid == player.uuid) & (Player.username == player.username)) # type: Player

            (PlayerRecordsRelationship.replace(
                player=saved_player,
                record=saved_server_record
            ).execute(database))


    return server




async def scrap_from_all_scrappers_and_save(*args, **kwargs):
    for servers in scrap_from_all_scrappers(*args, **kwargs):
        for server in servers:
            if server.host:
                saved = save_into_database(server=server, database=DATABASE)
                print("Saved:", saved)



async def ping_and_update(*args, **kwargs):
    async for servers in pinger.ping_all(*args, **kwargs):
        for server in servers:
            saved = save_into_database(server=server, database=DATABASE)
            print("Updated:", saved)



async def ping_from_all_scrappers_and_save(*args, **kwargs):
    for scrapped_servers in scrap_from_all_scrappers(*args, **kwargs):
        statuses = await asyncio.gather(*[
            pinger.get_status(scrapped_server) for scrapped_server in scrapped_servers if scrapped_server and scrapped_server.host
        ])
    
        for status in statuses:
            saved = save_into_database(server=status, database=DATABASE)
            print("Saved:", saved)



if __name__ == "__main__":
    if uvloop:
        uvloop.install()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(ping_from_all_scrappers_and_save())
    loop.close()
