import asyncio

from aiohttp import web
from discord import __version__ as discord_version
from discord.ext import commands


class WebServer(commands.Cog, name="WebServer"):
    def __init__(self, client: commands.Bot):
        self.client: commands.Bot = client
        self.status_channel = 1152780745270644738

    @commands.Cog.listener()
    async def on_ready(self):
        print("Webserver is running!")

    async def index_handler(self, request: web.Request) -> dict:
        return web.json_response(
            {
                "botStatus": "online",
                "discordVersion": discord_version,
                "botLatency": f"{self.client.get_bot_latency}ms",
                "botUptime": self.client.get_uptime,
            }
        )

    async def health_check(self, request: web.Request) -> None:
        return web.Response(text="SUP")

    async def webserver(self) -> None:
        app: web.Application = web.Application()
        app.router.add_get("/", self.index_handler)
        app.router.add_get("/health", self.health_check)
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
