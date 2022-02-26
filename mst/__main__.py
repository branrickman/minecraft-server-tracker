"""
    The cycle of this program:
        1. `scrappers.py` - Scraps Minecraft server IPs and ports from various online server listing sources.
        2. `data.py` - Saves the scrapped servers to database. No status is checked yet.
        3. `pinger.py` - Asynchronously ping multiple servers at once from the database and save the results.
"""

import typer

from mst.data import ping_from_all_scrappers_and_save


CLI = typer.Typer()


@CLI.command()
def all():
    asyncio.run(ping_from_all_scrappers_and_save())
    


if __name__ == "__main__":
    import asyncio
    try:
        import uvloop # type: ignore
    except ImportError:
        uvloop = None

    if uvloop:
        uvloop.install()


    CLI()
