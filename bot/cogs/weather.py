from __future__ import annotations

import os
from typing import Literal

from discord import Colour, Embed
from discord.ext import commands


class Weather(commands.Cog, name="Weather"):
    def __init__(self, client: commands.Bot) -> None:
        self.client: commands.Bot = client
        self.api_key: str = os.getenv("TOMORROW_API_KEY")

    @commands.hybrid_command(name="weather", aliases=["w"])
    async def weather(
        self,
        ctx: commands.Context,
        location: str,
        unit: Literal["metric", "imperial"] = "imperial",
    ) -> None:
        """
        Get the weather for a specified location.
        """
        if location is None:
            await ctx.send("You must specify a location.", ephemeral=True)
            return
        if unit not in ["metric", "imperial"]:
            await ctx.send("Please choose from, metric or imperial", ephemeral=True)
            return
        url = f"https://api.tomorrow.io/v4/weather/realtime?location={location}&units={unit}&apikey={self.api_key}"
        weather_data = await self.client.session.get(
            url, headers={"Accept": "application/json"}
        )
        if weather_data.status != 200:
            await ctx.send(
                "An error occurred while fetching the weather data.",
                ephemeral=True,
            )
            return
        weather_json = await weather_data.json()
        location_name = weather_json["location"]["name"]
        temp = weather_json["data"]["values"]["temperature"]
        feels_like = weather_json["data"]["values"]["temperatureApparent"]
        humidity = weather_json["data"]["values"]["humidity"]
        wind_speed = weather_json["data"]["values"]["windSpeed"]
        precipitation = weather_json["data"]["values"]["precipitationProbability"]

        embed = Embed()
        embed.title = f"Weather for {location_name}"
        embed.colour = Colour.blurple()
        embed.set_thumbnail(
            url="https://i.gyazo.com/4e8180c976a725a335cc9c3b00f5145e.jpg"
        )
        embed.add_field(name="Temperature", value=f"{temp}°")
        embed.add_field(name="Feels Like", value=f"{feels_like}°")
        embed.add_field(name="Humidity", value=f"{humidity}%")
        embed.add_field(name="Wind Speed", value=f"{wind_speed} mph")
        embed.add_field(name="Precipitation", value=f"{precipitation}%")
        embed.set_footer(text="Powered by Tomorrow.io")

        await ctx.send(embed=embed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(Weather(client))
