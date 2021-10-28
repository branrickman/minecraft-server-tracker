import typing as t

from dataclasses import dataclass
from mcstatus import MinecraftServer

from mst.scrappers import MinecraftMPScrapper



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



def ping_all(from_page: int=1, online_only: bool=True, with_uptime_higher_than: int=75):
    scrapper = MinecraftMPScrapper()

    for scrapped_servers in scrapper.scrap(from_page=from_page, online_only=online_only, with_uptime_higher_than=with_uptime_higher_than):
        for scrapped_server in scrapped_servers:
            ping_server = MinecraftServer(host=scrapped_server.host, port=scrapped_server.port)

            try:
                status = ping_server.status()

                pinged_server_status = PingedServerStatus(
                    description=status.description,
                    version=status.version.name,
                    latency=status.latency,
                    players=PingedPlayerList(
                        max=status.players.max,
                        online=status.players.online,
                        list=[PingedPlayer(uuid=player.id, username=player.name) for player in status.players.sample if player.id != '00000000-0000-0000-0000-000000000000']
                    ),
                    is_modded='modinfo' in status.raw
                )
        
            except Exception:
                pinged_server_status = None


            yield PingedServer(
                source=scrapped_server.source,
                host=scrapped_server.host,
                port=scrapped_server.port,
                online=True if pinged_server_status else scrapped_server.is_online,
                status=pinged_server_status
            )



if __name__ == "__main__":
    for result in ping_all(from_page=200, online_only=False, with_uptime_higher_than=1):
        print(result)
