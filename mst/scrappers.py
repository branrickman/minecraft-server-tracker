import typing as t

from requests_cache import CachedSession
from dataclasses import dataclass

from bs4 import BeautifulSoup



__all__ = ['ALL_SCRAPPERS', 'ScrappedServer', 'ServerListScrapper', 'MinecraftMPScrapper']


@dataclass
class ScrappedServer:
    host: t.Optional[str] = None
    port: int = 25565
    source: str = None



class ServerListScrapper():
    def __init__(self, url_template: str) -> None:
        self.url_template = url_template
        self.page = 1
        self.session = CachedSession(cache_name='requests_cache')

        self.soup = self.update_soup()



    @property
    def current_url(self) -> str:
        return self.url_template.format(page=self.page)


    def update_soup(self, *get_args, **get_kwargs) -> None:
        self.soup = BeautifulSoup(markup=self.session.get(self.current_url, *get_args, **get_kwargs).text, features='lxml')



    def scrap_page(self, page_number: int) -> t.List[ScrappedServer]:
        """
            Scraps all servers from a specific page of the server list and returns them as a list of `Server` objects.
        """

        raise NotImplementedError(page_number)


    def scrap(self, from_page: int=1, *args, **kwargs):
        # Yield infinitely, until there are no servers left:
        current_page = from_page
    
        while True:
            servers = self.scrap_page(current_page, *args, **kwargs)

            if not servers or len(servers) <= 0:
                break

            current_page += 1
            yield servers



class MinecraftMPScrapper(ServerListScrapper):
    def __init__(self) -> None:
        self.source = 'minecraft-mp.com'
        super().__init__(url_template="https://minecraft-mp.com/servers/updated/{page:d}/")


    def scrap_page(self, page_number: int) -> t.List[ScrappedServer]:
        self.page = page_number
        self.update_soup()

        all_servers: t.List[ScrappedServer] = []
        all_ips = self.soup.select(r'.container > table > tbody > tr > td:nth-child(2) > strong')

        for ip in all_ips:
            server_ip, _, server_port = ip.get_text(strip=True).lower().partition(':')

            all_servers.append(ScrappedServer(
                source=self.source,
                host=server_ip.lower() if server_ip != 'private server' else None,
                port=(int(server_port) if server_port.isdigit() else 25565)
            ))
    
        return all_servers



class MinecraftServerListScrapper(ServerListScrapper):
    def __init__(self) -> None:
        self.source = 'minecraft-server-list.com'
        super().__init__(url_template="https://minecraft-server-list.com/sort/PopularAllTime/page/{page:d}/")


    def scrap_page(self, page_number: int) -> t.List[ScrappedServer]:
        self.page = page_number
        self.update_soup()

        all_servers: t.List[ScrappedServer] = []
        all_ips = self.soup.select(r'.serverdatadiv1 > table > tbody > tr > .n2')


        is_enough = False
        # This server list has a strange behaviour to always return servers no matter on what page you are.
        # To prevent infinite loop of same servers, we only return them as long as there are max. of them at single page.
        if len(all_ips) < 25:
            is_enough = True


        for ip in all_ips:
            server_ip, _, server_port = ip['id'].strip().lower().partition(':')

            all_servers.append(ScrappedServer(
                source=self.source,
                host=server_ip.lower(),
                port=(int(server_port) if server_port.isdigit() else 25565)
            ))

            if is_enough:
                break


        return all_servers



class MinecraftServersScrapper(ServerListScrapper):
    def __init__(self) -> None:
        self.source = 'minecraftservers.org'
        super().__init__(url_template="https://minecraftservers.org/index/{page:d}/")


    def scrap_page(self, page_number: int) -> t.List[ScrappedServer]:
        self.page = page_number
        self.update_soup()

        all_servers: t.List[ScrappedServer] = []
        all_ips = self.soup.select(r'.server-ip > button')

        for ip in all_ips:
            server_ip, _, server_port = ip['data-clipboard-text'].strip().lower().partition(':')

            all_servers.append(ScrappedServer(
                source=self.source,
                host=server_ip.lower(),
                port=(int(server_port) if server_port.isdigit() else 25565)
            ))


        return all_servers



class ServersMinecraftScrapper(ServerListScrapper):
    def __init__(self) -> None:
        self.source = 'servers-minecraft.com'
        super().__init__(url_template="https://servers-minecraft.com/page/{page:d}")


    def scrap_page(self, page_number: int) -> t.List[ScrappedServer]:
        self.page = page_number
        self.update_soup()

        all_servers: t.List[ScrappedServer] = []
        all_ips = self.soup.select(r'.banner-ip button.copy')

        for ip in all_ips:
            server_ip, _, server_port = ip['data-clipboard-text'].strip().partition(':')

            all_servers.append(ScrappedServer(
                source=self.source,
                host=server_ip.lower(),
                port=(int(server_port) if server_port.isdigit() else 25565)
            ))


        return all_servers



class MinecraftListScrapper(ServerListScrapper):
    def __init__(self) -> None:
        self.source = 'minecraftlist.org'
        super().__init__(url_template="https://minecraftlist.org/servers?order_by=server_id&page={page:d}")


    def scrap_page(self, page_number: int) -> t.List[ScrappedServer]:
        self.page = page_number
        self.update_soup()

        all_servers: t.List[ScrappedServer] = []
        all_ips = self.soup.select(r'.mcp-banner input.server-address')


        is_enough = False
        # This server list has a strange behaviour to always return servers no matter on what page you are.
        # To prevent infinite loop of same servers, we only return them as long as there are max. of them at single page.
        if len(all_ips) < 20:
            is_enough = True


        for ip in all_ips:
            server_ip, _, server_port = ip['value'].strip().partition(':')

            all_servers.append(ScrappedServer(
                source=self.source,
                host=server_ip.lower(),
                port=(int(server_port) if server_port.isdigit() else 25565)
            ))

            if is_enough:
                break


        return all_servers



class MinecraftServersListScrapper(ServerListScrapper):
    def __init__(self) -> None:
        self.source = 'minecraft-servers-list.org'
        super().__init__(url_template="https://www.minecraft-servers-list.org/rank/{page:d}")


    def scrap_page(self, page_number: int) -> t.List[ScrappedServer]:
        self.page = page_number
        self.update_soup()

        all_servers: t.List[ScrappedServer] = []
        all_ips = self.soup.select(r'.container > table:nth-last-child(2) .copy-ip-trigger')


        is_enough = False
        # This server list has a strange behaviour to always return servers no matter on what page you are.
        # To prevent infinite loop of same servers, we only return them as long as there are max. of them at single page.
        if len(all_ips) < 19:
            is_enough = True


        for ip in all_ips:
            server_ip, _, server_port = ip['data-clipboard-text'].strip().partition(':')

            all_servers.append(ScrappedServer(
                source=self.source,
                host=server_ip.lower(),
                port=(int(server_port) if server_port.isdigit() else 25565)
            ))

            if is_enough:
                break


        return all_servers



ALL_SCRAPPERS: t.List[t.Type[ServerListScrapper]] = [
    MinecraftMPScrapper,
    MinecraftServerListScrapper,
    MinecraftServersScrapper,
    ServersMinecraftScrapper,
    MinecraftListScrapper,
    MinecraftServersListScrapper
]

def scrap_from_all_scrappers(scrappers: t.List[t.Type[ServerListScrapper]]=ALL_SCRAPPERS, *args, **kwargs):
    """
        Reference: https://stackoverflow.com/a/69748260/12422061
    """

    i = 0
    n = len(scrappers)
    generators = [generator().scrap(*args, **kwargs) for generator in scrappers]

    while generators:
        try:
            yield next(generators[i % n])
            i += 1

        except StopIteration:
            generators.pop(i % n)
            n -= 1



if __name__ == "__main__":
    import asyncio
    try:
        import uvloop # type: ignore
    except ImportError:
        uvloop = None

    from mst.data import scrap_from_all_scrappers_and_save

    if uvloop:
        uvloop.install()

    asyncio.run(scrap_from_all_scrappers_and_save())
