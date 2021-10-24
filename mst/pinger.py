from mcstatus import MinecraftServer

from mst.scrappers import MinecraftMPScrapper



def ping_all(from_page: int=1):
    scrapper = MinecraftMPScrapper()

    for servers in scrapper.scrap(from_page=from_page):
        for server in servers:
            server_status = MinecraftServer(host=server.host, port=server.port)

            try:
                status = server_status.status()
                status = {
                    "description": status.description,
                    "version": status.version.name,
                    "latency": f"{status.latency} ms",
                    "players": {
                        "max": status.players.max,
                        "online": status.players.online,
                        "list": [{player.id: player.name} for player in status.players.sample if player.id != '00000000-0000-0000-0000-000000000000']
                    },
                    "modded": 'modinfo' in status.raw
                }
        
            except Exception:
                status = {}


            yield {
                "source": server.source,
                "host": server.host,
                "port": server.port,
                "status": status
            }



if __name__ == "__main__":
    for result in ping_all():
        print(result)
