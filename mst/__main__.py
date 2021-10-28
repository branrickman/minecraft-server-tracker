"""
    The cycle:
        1. `scrappers.py`
        2. `pinger.py`
        3.1. `database.py`
            3.2. `save.py`
"""

import asyncio

from mst.save import scrap_from_all_and_save



if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scrap_from_all_and_save())
    loop.close()
