import typing as t

from datetime import timedelta
from requests_cache import CachedSession
from bs4 import BeautifulSoup

from mst.orm import Server



class ServerListScrapper():
    def __init__(self, url_template: str, source: t.Optional[str]=None) -> None:
        self.session = CachedSession(cache_name='requests_cache', expire_after=timedelta(hours=2))

        self.url_template = url_template
        self.source = source

        self.page = 1
        self.max_pages = self._get_max_pages()

        self.soup = self.update_soup()


    @property
    def current_url(self) -> str:
        return self.url_template.format(page=self.page)


    def update_soup(self, *get_args, **get_kwargs) -> None:
        self.soup = BeautifulSoup(markup=self.session.get(self.current_url, *get_args, **get_kwargs).text, features='lxml')


    def move_to_page(self, page_number: int, *args, **kwargs):
        self.page = page_number
        self.update_soup(*args, **kwargs)


    def _get_max_pages(self) -> t.Optional[int]:
        """
            Overwrite this function to implement your own logic to determine the max page count a server list has.

            Some server lists are dum dum and return servers no matter on what page you are (instead of showing a good, old 404).
        """

        return None


    def scrap_page(self) -> t.List[Server]:
        """
            Scraps all servers from a specific page of the server list and returns them as a list of `Server` objects.
        """

        raise NotImplementedError()


    def scrap(self, *args, **kwargs) -> t.Generator[t.List[Server], None, None]:
        """
            Scraps all pages until there are no servers left.
        """
    
        current_page = self.page

        while True:
            servers = self.scrap_page(current_page, *args, **kwargs)

            # If there are no servers, stop:
            if not servers or len(servers) <= 0:
                break

            current_page += 1
            yield servers

            # Stop, if we know max_pages:
            _max = getattr(self, 'max_pages', None)
            if _max is not None and current_page >= _max:
                break



class MinecraftMPScrapper(ServerListScrapper):
    def __init__(self) -> None:
        super().__init__(url_template="https://minecraft-mp.com/servers/updated/{page:d}/", source='minecraft-mp.com')


    def scrap_page(self, page_number: int) -> t.List[Server]:
        self.move_to_page(page_number)

        all_servers: t.List[Server] = []
        all_ips = self.soup.select(r'.container > table > tbody > tr > td:nth-child(2) > strong')

        for ip in all_ips:
            server_ip, _, server_port = ip.get_text(strip=True).lower().partition(':')

            all_servers.append(Server(
                source=self.source,
                host=server_ip.lower() if server_ip != 'private server' else None,
                port=(int(server_port) if server_port.isdigit() else 25565)
            ))
    
        return all_servers



class MinecraftServerListScrapper(ServerListScrapper):
    def __init__(self) -> None:
        super().__init__(url_template="https://minecraft-server-list.com/sort/PopularAllTime/page/{page:d}", source='minecraft-server-list.com')


    def _get_max_pages(self) -> t.Optional[int]:
        self.move_to_page(1)
        _raw = self.soup.select_one(r'.paginate > ul > li:nth-last-child(1) > a')

        if _raw:
            return int(_raw['href'].removeprefix('/sort/PopularAllTime/page/').removesuffix('/'))


    def scrap_page(self, page_number: int) -> t.List[Server]:
        self.move_to_page(page_number)

        all_servers: t.List[Server] = []
        all_ips = self.soup.select(r'.serverdatadiv1 > table > tbody > tr > .n2')


        for ip in all_ips:
            server_ip, _, server_port = ip['id'].strip().lower().partition(':')

            all_servers.append(Server(
                source=self.source,
                host=server_ip.lower(),
                port=(int(server_port) if server_port.isdigit() else 25565)
            ))


        return all_servers



class MinecraftServersScrapper(ServerListScrapper):
    def __init__(self) -> None:
        super().__init__(url_template="https://minecraftservers.org/index/{page:d}", source='minecraftservers.org')


    def scrap_page(self, page_number: int) -> t.List[Server]:
        self.move_to_page(page_number)

        if self.max_pages and self.page >= self.max_pages:
            return []


        all_servers: t.List[Server] = []
        all_ips = self.soup.select(r'.server-ip > button')

        for ip in all_ips:
            server_ip, _, server_port = ip['data-clipboard-text'].strip().lower().partition(':')

            all_servers.append(Server(
                source=self.source,
                host=server_ip.lower(),
                port=(int(server_port) if server_port.isdigit() else 25565)
            ))


        return all_servers



class ServersMinecraftScrapper(ServerListScrapper):
    def __init__(self) -> None:
        super().__init__(url_template="https://servers-minecraft.com/page/{page:d}", source='servers-minecraft.com')


    def _get_max_pages(self) -> t.Optional[int]:
        self.move_to_page(1)
        _raw = self.soup.select_one(r'ul.pagination > li:nth-last-child(1) > a')

        if _raw:
            return int(_raw['href'].removeprefix('/page/'))


    def scrap_page(self, page_number: int) -> t.List[Server]:
        self.move_to_page(page_number)

        all_servers: t.List[Server] = []
        all_ips = self.soup.select(r'.banner-ip button.copy')

        for ip in all_ips:
            server_ip, _, server_port = ip['data-clipboard-text'].strip().partition(':')

            all_servers.append(Server(
                source=self.source,
                host=server_ip.lower(),
                port=(int(server_port) if server_port.isdigit() else 25565)
            ))


        return all_servers



class MinecraftListScrapper(ServerListScrapper):
    def __init__(self) -> None:
        super().__init__(url_template="https://minecraftlist.org/servers?order_by=server_id&page={page:d}", source='minecraftlist.org')


    def _get_max_pages(self) -> t.Optional[int]:
        self.move_to_page(1)
        _raw = self.soup.select_one(r'ul.pagination > li:nth-last-child(2) > a')

        if _raw:
            return int(_raw.get_text(strip=True))


    def scrap_page(self, page_number: int) -> t.List[Server]:
        self.move_to_page(page_number)

        all_servers: t.List[Server] = []
        all_ips = self.soup.select(r'.mcp-banner input.server-address')


        for ip in all_ips:
            server_ip, _, server_port = ip['value'].strip().partition(':')

            all_servers.append(Server(
                source=self.source,
                host=server_ip.lower(),
                port=(int(server_port) if server_port.isdigit() else 25565)
            ))


        return all_servers



class MinecraftServersListScrapper(ServerListScrapper):
    def __init__(self) -> None:
        super().__init__(url_template="https://www.minecraft-servers-list.org/rank/{page:d}", source='minecraft-servers-list.org')


    def _get_max_pages(self) -> t.Optional[int]:
        self.move_to_page(1)
        _raw = self.soup.select_one(r'ul.pagination > li:nth-last-child(2) > a')

        if _raw:
            return int(_raw.get_text(strip=True))


    def scrap_page(self, page_number: int) -> t.List[Server]:
        self.move_to_page(page_number)

        all_servers: t.List[Server] = []
        all_ips = self.soup.select(r'.container > table:nth-last-child(2) .copy-ip-trigger')


        for ip in all_ips:
            server_ip, _, server_port = ip['data-clipboard-text'].strip().partition(':')

            all_servers.append(Server(
                source=self.source,
                host=server_ip.lower(),
                port=(int(server_port) if server_port.isdigit() else 25565)
            ))


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
