import datetime
from aiohttp import web
from discord import __version__ as discord_version, Webhook, Embed
from discord.ext import commands


class WebServer(commands.Cog, name="WebServer"):
    def __init__(self, client: commands.Bot):
        self.client: commands.Bot = client

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

    async def webhook(self, request: web.Request) -> None:
        data = await request.json()
        status_mapping = {"down": ":x: Down", "up": ":white_check_mark: Up"}
        status = data["status"]
        channel = self.client.get_channel(1152780745270644738)
        webhook = await channel.create_webhook(name="Health Check")
        async with self.client.session as session:
            discord_webhook = Webhook.from_url(webhook.url, session=session)
            embed = Embed(title=data["name"], color=242424, timestamp=datetime.datetime.utcnow())
            if status in status_mapping:
                embed.add_field(name="Status", value=status_mapping[status])
                embed.set_author(name="Health Check - WiseOldMan")
            embed.set_footer(text="Provided by healthchecks.io")
            await discord_webhook.send(username="WiseOldMan", embeds=[embed], avatar_url=self.client.logo_url)
            return web.Response(text="SUP")

    async def webserver(self) -> None:
        app: web.Application = web.Application()
        app.router.add_get("/", self.index_handler)
        app.router.add_get("/health", self.health_check)
        app.router.add_post("/webhook", self.webhook)
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
