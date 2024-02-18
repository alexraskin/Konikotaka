import asyncio
import os
import time
from datetime import datetime

import aiohttp_cors  # type: ignore
from aiohttp import web
from discord.ext import commands
from models.users import DiscordUser
from sqlalchemy.future import select  # type: ignore


class WebServer(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client
        self.api_key: str = os.environ["X-API-KEY"]

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        self.client.log.info("Webserver is started successfully.")

    async def get_api_latency(self) -> int:
        start_time = time.time()
        await self.client.session.get("https://api.twizy.sh/")
        end_time = time.time()
        latency: int = round((end_time - start_time) * 1000)
        return latency

    async def get_all_commands(self) -> list:
        commands: list = []
        for command in self.client.commands:
            if command.hidden is False:
                commands.append({"name": command.name, "description": command.help})
        return commands

    async def index_handler(self, request: web.Request) -> web.Response:
        return web.json_response(
            {
                "last_fetch": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "@me": {"botStatus": 200, "upTime": str(self.client.get_uptime)},
                "gitRevision": self.client.git_revision,
                "ram": f"{self.client.memory_usage}MB",
                "cpu": f"{self.client.cpu_usage}%",
                "ping": {
                    "type": "ms",
                    "bot": self.client.get_bot_latency,
                    "rest": await self.get_api_latency(),
                },
                "botCommands": await self.get_all_commands(),
            }
        )

    async def leaderboard_handler(self, request: web.Request) -> web.Response:
        async with self.client.async_session() as session:
            async with session.begin():
                query = await session.execute(
                    select(DiscordUser).order_by(DiscordUser.level.desc())
                )
                users: DiscordUser = query.scalars().all()
                leaderboard = []
                for user in users:
                    leaderboard.append({"username": user.username, "level": user.level})
                return web.json_response(leaderboard)

    async def health_check(self, request: web.Request) -> web.Response:
        return web.json_response({"status": "healthy"})

    async def webserver(self) -> None:
        app: web.Application = web.Application()
        app.router.add_get("/", self.index_handler)
        app.router.add_get("/leaderboard", self.leaderboard_handler)
        app.router.add_get("/health", self.health_check)
        cors = aiohttp_cors.setup(
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

    def __unload(self) -> None:
        asyncio.ensure_future(self.site.stop())


async def setup(client: commands.Bot) -> None:
    server: WebServer = WebServer(client)
    client.loop.create_task(server.webserver())
    await client.add_cog(WebServer(client))
