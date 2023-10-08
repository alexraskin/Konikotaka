import asyncio
import os
import time
from datetime import datetime

import aiohttp_cors
import pytz
from aiohttp import web
from discord.ext import commands, tasks
from models.ping import Ping
from sqlalchemy.future import select


class WebServer(commands.Cog, name="WebServer"):
    def __init__(self, client: commands.Bot):
        self.client: commands.Bot = client
        self.pid: int = os.getpid()
        self.api_key: str = os.getenv("X-API-KEY")

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.client.log.info("Webserver is started!")
        self.update_latency.start()

    @tasks.loop(minutes=1)
    async def update_latency(self):
        ping: Ping = Ping(
            ping_ws=self.client.get_bot_latency,
            ping_rest=await self.get_api_latency(),
            date=datetime.utcnow(),
        )
        async with self.client.async_session() as session:
            async with session.begin():
                try:
                    session.add(ping)
                    await session.flush()
                    await session.commit()
                except Exception as e:
                    self.client.log.error(e)
                    await session.rollback()

    async def get_ping_history(self) -> list:
        async with self.client.async_session() as session:
            async with session.begin():
                query: select = select(Ping).order_by(Ping.id.desc()).limit(25)
                try:
                    result = await session.execute(query)
                except Exception as e:
                    self.client.log.error(e)
                    return []
                data = result.scalars().all()
                for k, v in enumerate(data):
                    data[k] = {
                        "ping_ws": v.ping_ws,
                        "ping_rest": v.ping_rest,
                        "date": v.date.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                return data

    async def get_discord_status(self) -> dict:
        discord_status = await self.client.session.get(
            "https://discordstatus.com/api/v2/status.json"
        )
        data = await discord_status.json()
        indicator: str = data["status"]["indicator"]
        description: str = data["status"]["description"]
        last_updated: str = data["page"]["updated_at"]
        input_datetime = datetime.fromisoformat(last_updated)
        input_datetime_utc = input_datetime.astimezone(pytz.utc)
        pretty_datetime_str: str = input_datetime_utc.strftime("%Y-%m-%d %H:%M:%S %Z")
        return {
            "indicator": indicator,
            "description": description,
            "lastUpdated": pretty_datetime_str,
        }

    async def get_api_latency(self) -> int:
        start_time: time = time.time()
        await self.client.session.get("https://api.twizy.dev/health")
        end_time: time = time.time()
        latency: int = round((end_time - start_time) * 1000)
        return latency

    async def index_handler(self, request: web.Request) -> web.json_response:
        return web.json_response({"status": "healthy"})

    async def stats_handler(self, request: web.Request) -> web.json_response:
        if request.headers.get("X-API-KEY") != self.api_key:
            return web.json_response({"error": "Invalid API key"})
        data: dict = {
            "_data": {
                "@me": {
                    "botStatus": 200,
                    "avatarUrl": self.client.user.avatar.url,
                    "botName": self.client.user.name,
                    "discriminator": self.client.user.discriminator,
                    "botId": self.client.user.id,
                },
                "ram": f"{self.client.memory_usage}MB",
                "git_revision": self.client.git_revision,
                "_last_fetch": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "cache": 60,
                "ping": {
                    "type": "ms",
                    "bot": self.client.get_bot_latency,
                    "rest": await self.get_api_latency(),
                },
                "discordStatus": await self.get_discord_status(),
                "history": [await self.get_ping_history()],
            }
        }
        return web.json_response(data)

    async def health_check(self, request: web.Request) -> web.json_response:
        return web.json_response({"status": "healthy"})

    async def webserver(self) -> None:
        app: web.Application = web.Application()
        app.router.add_get("/", self.index_handler)
        app.router.add_get("/stats", self.stats_handler)
        app.router.add_get("/health", self.health_check)
        cors: aiohttp_cors = aiohttp_cors.setup(
            app,
            defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                    allow_methods=["GET"],
                    max_age=3600,
                )
            },
        )
        for route in list(app.router.routes()):
            cors.add(route)
        runner: web.AppRunner = web.AppRunner(app)
        await runner.setup()
        self.site: web.TCPSite = web.TCPSite(runner, "0.0.0.0", 8000)
        await self.client.wait_until_ready()
        await self.site.start()

    def __unload(self):
        asyncio.ensure_future(self.site.stop())


async def setup(client: commands.Bot):
    server: WebServer = WebServer(client)
    client.loop.create_task(server.webserver())
    await client.add_cog(WebServer(client))
