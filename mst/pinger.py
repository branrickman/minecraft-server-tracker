"""
    Server pinging utitilites.
    Note: Windows sometimes raises `OSError: An operation was attempted on something that is not a socket` when running in asyncio. This was reported
    here: https://bugs.python.org/issue43253, and it seems to be Windows related only (works fine on Linux).

    Note #2: This is my first time using `asyncio`, where stuff actually works. I admit that it is hard, and that any PRs for optimizations are welcome.
"""

import typing as t

import asyncio
try:
    import uvloop # type: ignore
except ImportError:
    uvloop = None

from dataclasses import dataclass
from mcstatus import MinecraftServer
from peewee import Database

from mst.settings import PLAYER_USERNAME_REGEX
from mst.scrappers import ScrappedServer



@dataclass
class PingedPlayer:
    uuid: str
    username: str



@dataclass
class PingedPlayerList:
    max: int
    online: int
    list: t.List[PingedPlayer]



@dataclass
class PingedServerStatus:
    description: str
    version: str
    latency: float
    players: PingedPlayerList
    is_modded: bool



@dataclass
class PingedServer:
    source: str
    host: str
    port: int
    online: bool = False
    status: t.Optional[PingedServerStatus] = None



# Circular:
from mst.data import DATABASE, yield_servers_from_database

async def async_ping_all(from_database: Database=DATABASE, at_once: int=25):
    async def __get_status(scrapped_server: ScrappedServer):
        try:
            status = await MinecraftServer(host=scrapped_server.host, port=scrapped_server.port).async_status()

            pinged_server_status = PingedServerStatus(
                description=status.description,
                version=status.version.name,
                latency=status.latency,
                players=PingedPlayerList(
                    max=status.players.max,
                    online=status.players.online,
                    list=[PingedPlayer(uuid=player.id, username=player.name) for player in status.players.sample if PLAYER_USERNAME_REGEX.match(player.username)] if status.players.sample else []
                ),
                is_modded='modinfo' in status.raw
            )
    
        except Exception:
            pinged_server_status = None


        return PingedServer(
            source=scrapped_server.source,
            host=scrapped_server.host,
            port=scrapped_server.port,
            online=pinged_server_status is not None,
            status=pinged_server_status
        )


    for scrapped_servers in yield_servers_from_database(database=from_database, at_once=at_once):
        statuses = await asyncio.gather(*[
            __get_status(scrapped_server) for scrapped_server in scrapped_servers if scrapped_server and scrapped_server.host
        ])
    
        yield statuses

            

if __name__ == "__main__":
    if uvloop:
        uvloop.install()

    async def main():
        async for servers in async_ping_all(online_only=False, with_uptime_higher_than=1):
            for server in servers:
                print(server)


    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
