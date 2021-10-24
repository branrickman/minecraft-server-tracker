from mcstatus import MinecraftServer

from mst.scrappers import MinecraftMPScrapper



def ping_all():
    scrapper = MinecraftMPScrapper()

    for servers in scrapper.scrap():
        for server in servers:
            try:
                pinger = MinecraftServer(host=server.host, port=server.port).status()
                status = {
                    "description": pinger.description,
                    "version": pinger.version.name,
                    "latency": f"{pinger.latency} ms",
                    "players": {
                        "max": pinger.players.max,
                        "online": pinger.players.online,
                        "list": [{player.id: player.name} for player in pinger.players.sample if player.id != '00000000-0000-0000-0000-000000000000']
                    }
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
