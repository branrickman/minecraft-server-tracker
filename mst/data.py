import typing as t

import asyncio
try:
    import uvloop # type: ignore
except ImportError:
    uvloop = None

from peewee import Database

from mst.pinger import PingedServer
from mst.database import Player, PlayerRecordsRelationship, Server, ServerRecord, initialize_database
from mst.scrappers import ScrappedServer, scrap_from_all


DATABASE = initialize_database()



def yield_servers_from_database(database: Database=DATABASE, at_once: int=25) -> t.Generator[t.List[Server], None, None]:
    query = (Server.select().bind(database)) # type: t.Iterator[Server]
    servers: t.List[Server] = []

    for server in query:
        if len(servers) < at_once:
            servers.append(server)
            continue

        yield servers
        servers.clear()



# TODO: create generic "server" class
def save_into_database(server: t.Union[PingedServer, ScrappedServer], database: Database=DATABASE):
    (Server.replace(
        hostname=server.host,
        port=server.port,
        source=server.source
    ).execute(database))
    saved_server = Server.get((Server.hostname == server.host) & (Server.port == server.port)) # type: Server

    if hasattr(server, 'status'):
        (ServerRecord.replace(
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




async def scrap_from_all_and_save(*args, **kwargs):
    for servers in scrap_from_all(*args, **kwargs):
        for server in servers:
            if server.host:
                saved = save_into_database(server=server, database=DATABASE)
                print("Saved:", saved)



if __name__ == "__main__":
    TEST = False

    if TEST:
        for servers in yield_servers_from_database():
            for server in servers:
                print(f"{server.ip_address}:")

                for record in server.records:
                    for player in record.get_players():
                        print(f"\t- {player.username}")
    
    else:
        if uvloop:
            uvloop.install()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(scrap_from_all_and_save())
        loop.close()
