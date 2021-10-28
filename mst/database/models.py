"""
    The models are divided into 2 main categories:
    - Normal models
    - Record models

    **Normal** models hold data that is constant and never changes, such as server address or player username.
    Although you can change this data, from the perspective of this scrapper, it is permanent since I'm not going to build some advanced systems
    for username histories (because there are tools like [NameMC](https://namemc.com/) for that purpose already) or server IP address history
    (because there is no way for the scrapper to know past IPs).

    **Record** models hold data that can change over time, such as server version (server can update to a new version), server MOTD/description
    (can be changed in server properties), player count, etc.
"""

from datetime import datetime

from peewee import *


__all__ = ['Record', 'ServerRecord', 'Player']



class Server(Model):
    """
        - Hostname
        - Port
        - Source (from what page was the server scrapped)
    """



class Record(Model):
    """
        - `timestamp` - The timestamp of the record
    """

    timestamp = DateTimeField(default=datetime.now)



class ServerRecord(Record):
    """
      - `latency` - Server latency (in ms)
      - `version` - Server version
      - `is_modded` - Is the server modded?
      - Server MOTD/description
      - Max players online
      - Players online (number)
      - Players online (list)
    """



class Player(Model):
    """
        - UUID
        - Username
        - Seen `x` times
        - Last seen at (datetime)
        - Last seen at (***server)
    """
