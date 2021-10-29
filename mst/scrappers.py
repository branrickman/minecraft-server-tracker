import typing as t

import requests
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

        self.soup = self.update_soup()



    @property
    def current_url(self) -> str:
        return self.url_template.format(page=self.page)


    def update_soup(self, *get_args, **get_kwargs) -> None:
        self.soup = BeautifulSoup(markup=requests.get(self.current_url, *get_args, **get_kwargs).text, features='html.parser')



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
        all_server_elements = self.soup.select(r'.container > table > tbody > tr')

        for server_element in all_server_elements:
            server_ip, _, server_port = server_element.select_one(r'td:nth-child(2) > strong').get_text(strip=True).lower().partition(':')

            all_servers.append(ScrappedServer(
                source=self.source,
                host=server_ip if server_ip != 'private server' else None,
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
        all_server_elements = self.soup.select(r'#site-wrapper div.serverdatadiv1 > table > tbody > tr')


        # MSL has a strange behaviour to always return last servers no matter on what page you are.
        # To prevent infinite loop of same servers, we only return them as long as there are 25 (or more) of them
        # (which means that there are more unique servers after that page -> 25 servers/per page).
        if len(all_server_elements) < 25:
            return []


        for server_element in all_server_elements:
            _n2 = server_element.select_one(r'.n2')
            if not _n2:
                continue

            server_ip, _, server_port = _n2['id'].partition(':')

            all_servers.append(ScrappedServer(
                source=self.source,
                host=server_ip,
                port=(int(server_port) if server_port.isdigit() else 25565)
            ))
    
        return all_servers



class MinecraftServersScrapper(ServerListScrapper):
    def __init__(self) -> None:
        self.source = 'minecraftservers.org'
        super().__init__(url_template="https://minecraftservers.org/index/{page:d}/")


    def scrap_page(self, page_number: int) -> t.List[ScrappedServer]:
        self.page = page_number
        self.update_soup()

        all_servers: t.List[ScrappedServer] = []
        all_server_elements = self.soup.select(r'#main .serverlist:nth-last-child(1) > tbody > tr')

        for server_element in all_server_elements:
            server_ip, _, server_port = server_element.select_one(r'.col-server > .server-ip > button')['data-clipboard-text'].strip().partition(':')

            all_servers.append(ScrappedServer(
                source=self.source,
                host=server_ip,
                port=(int(server_port) if server_port.isdigit() else 25565)
            ))
    
        return all_servers



ALL_SCRAPPERS: t.List[t.Type[ServerListScrapper]] = [MinecraftMPScrapper, MinecraftServerListScrapper, MinecraftServersScrapper]

def scrap_from_all(scrappers: t.List[t.Type[ServerListScrapper]]=ALL_SCRAPPERS, *args, **kwargs):
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
    for servers in scrap_from_all():
        for server in servers:
            print(server)
