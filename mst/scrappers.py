import typing as t

import requests
from dataclasses import dataclass
from bs4 import BeautifulSoup



@dataclass
class ScrappedServer:
    host: t.Optional[str] = None
    port: int = 25565
    is_online: bool = False
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


    def scrap(self) -> t.Generator[t.List[ScrappedServer], None, None]:
        """
            Scraps all servers from all pages of the entire server list and yields them as lists of `Server` objects.
        """

        raise NotImplementedError()



class MinecraftMPScrapper(ServerListScrapper):
    def __init__(self) -> None:
        self.source = 'MinecraftMP'
        super().__init__(url_template="https://minecraft-mp.com/servers/updated/{page:d}/")



    def scrap_page(self, page_number: int, online_only: bool=True, with_uptime_higher_than: int=75) -> t.List[ScrappedServer]:
        self.page = page_number
        self.update_soup()

        all_servers: t.List[ScrappedServer] = []
        all_server_elements = self.soup.select(r'.container > table')[0].select(r'tbody > tr')

        for server_element in all_server_elements:
            if isinstance(with_uptime_higher_than, (int, float)):
                try:
                    uptime = int(server_element.select_one(r'td:nth-child(4) > span.badge').get_text().strip('%'))

                    if uptime <= with_uptime_higher_than:
                        continue

                except Exception:
                    continue

            is_online = (server_element.select_one(r'td:nth-child(2) > span.badge').get_text(strip=True) == 'Online')

            if online_only and not is_online:
                continue

            server_ip, _, server_port = server_element.select_one(r'td:nth-child(2) > strong').get_text().lower().strip().partition(':')

            all_servers.append(ScrappedServer(
                source=self.source,
                host=server_ip if server_ip != 'private server' else None,
                is_online=is_online,
                port=(int(server_port) if server_port.isdigit() else 25565)
            ))
    
        return all_servers


    def scrap(self, from_page: int=1, online_only: bool=True, with_uptime_higher_than: int=75) -> t.Generator[t.List[ScrappedServer], None, None]:
        try:
            max_pages = int(self.soup.select_one(r'.pagination > li:nth-last-child(2) > a').get_text())

        except Exception:
            max_pages = 500

        for page in range(from_page, max_pages):
            servers = self.scrap_page(page_number=page, online_only=online_only, with_uptime_higher_than=with_uptime_higher_than)

            if len(servers) <= 0:
                break

            yield servers



if __name__ == "__main__":
    for servers in MinecraftMPScrapper().scrap():
        for server in servers:
            print(server.host, server.port)
