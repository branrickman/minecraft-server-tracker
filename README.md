# Minecraft Server Tracker

An open source Python 3.9 tool to massively scrap all publicly listed servers from various server lists, ping them and save the results into a database.

### Currently, it can:
  - Build SQLite databases of scrapped servers of your choice
  - Create records of scrapped servers and assign timestamps to them. One server can have as much records as you want - they will all be tied together in the database, where they can be fetched, joined and read.
  - **The following data is scrapped:**
      - Server IP address/hostname and port
      - Source (from what webpage was it scraped), version, latency, whether the server is modded or not, MOTD, max player count and online player count
      - Player list along with UUIDs
  - Pinging is done asynchronously, to be as fast as possible (scraping and pinging ~40,000 servers from 3 server lists takes about 1 hour)
  - And more(?)


**Note** that some plugins/mods may alter what data is sent to the client/this tool through packet manipulation. This means that we have no way to determine whether a fact is true or false when scrapping the servers. For example, if a server says that it is running vanilla, but in fact is running Fabric, this tool says that it runs vanilla. If that server says that it has 1,000 players online but actually doesn't have any, it doesn't matter as this tool will say that it has 1,000 players instead.

Also, check `TODO` and `mst/settings.py`.


### A word about this project:

Recently, I saw FitMC's [video about the Copenheimer project](https://www.youtube.com/watch?v=hoS0PM20KJk). Because I am a data maniac and I like to hoard data myself, I thought that this was a really cool idea. Sadly for me, it isn't open source and the database it was using is private. So I thought: "I can do this too!". And so I tried.

Please note that I am not affiliated with the Copenheimer project in any way. I've never even played at 2b2t and barerly play Minecraft at all. Understand that this tool was primarily made out of curiosity, and later evolved into me learning how to do asynchronous programming in Python (yes, this is my first time doing it, so if it's weird, please excuse me). The data scraped by this tool is listed publicly on server lists, so anyone can view it anyways (this tool does not scrap private/unlisted servers). Morever, this program doesn't make a bot join the server to scan it further. It only fetches the information that is available in your client's server list (by using [Dinnerbone's MCStatus library](https://github.com/Dinnerbone/mcstatus)).

I never intend this to be used for malicious purposes, such as spreading damage over innocent Minecraft servers. The project served me well by teaching me more about asynchronous programming in Python (and it is my first project that uses [asyncio](https://docs.python.org/3/library/asyncio.html)). **Use this at your own risk!**

First working-as-intended version was made in roughly 5 days (at time of me writing this). It is messy, but gets the job done. If you have ideas or PRs, please create an issue for them. This project will likely be under minimal maintenance, since I don't really have much to do with it and I want to focus on other Python projects. That's also why this project's code structure is quite messy. But it just works.

Use wisely with caution.
