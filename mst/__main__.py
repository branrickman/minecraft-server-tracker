"""
    The cycle of this program:
        1. `scrappers.py` - Scraps Minecraft server IPs and ports from various online server listing sources.
        2. `data.py` - Saves the scrapped servers to database. No status is checked yet.
        3. `pinger.py` - Asynchronously ping multiple servers at once from the database and save the results.
    
    Use `python -m mst` to run. CLI will come soon (as mentioned in the `TODO` file)

    **Some statistics:**
    - Scrapping entire MinecraftMP server list takes about 
"""

import asyncio
try:
    import uvloop # type: ignore
except ImportError:
    uvloop = None

from mst.data import ping_and_update, ping_from_all_scrappers_and_save



if __name__ == "__main__":
    if uvloop:
        uvloop.install()

    loop = asyncio.get_event_loop()

    MODE = 0
    if MODE == 0:
        loop.run_until_complete(ping_from_all_scrappers_and_save())
    else:
        loop.run_until_complete(ping_and_update())

    loop.close()
