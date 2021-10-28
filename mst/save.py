import typing as t

import asyncio
try:
    import uvloop # type: ignore
except ImportError:
    uvloop = None

from peewee import Database

from mst.database import Player, PlayerRecordsRelationship, Server, ServerRecord, initialize_database
from mst.pinger import PingedServer, async_ping_all
from mst.scrappers import ALL_SCRAPPERS, MinecraftMPScrapper, ServerListScrapper


DATABASE = initialize_database()



def save_into_database(servers: t.List[PingedServer], database: Database=DATABASE):
    for server in servers:
        (Server.replace(
            hostname=server.host,
            port=server.port,
            source=server.source
        ).execute(database))

        saved_server = Server.get((Server.hostname == server.host) & (Server.port == server.port)) # type: Server

        if server.status:
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


    return servers


async def scrap_and_save(database: Database=DATABASE, scrapper: t.Type[ServerListScrapper]=MinecraftMPScrapper(), from_page: int=1, *args, **kwargs):
    async for servers in async_ping_all(scrapper=scrapper, from_page=from_page, *args, **kwargs):
        yield save_into_database(servers=servers, database=database)


async def scrap_from_all_and_save(*args, **kwargs):
    for scrapper in ALL_SCRAPPERS:
        async for pinged_servers in scrap_and_save(scrapper=scrapper(), *args, **kwargs):
            for pinged_server in pinged_servers:
                print(f"Saving: {pinged_server.host}:{pinged_server.port} ({pinged_server.source})")



if __name__ == "__main__":
    if uvloop:
        uvloop.install()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(scrap_from_all_and_save())
    loop.close()
