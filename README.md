# RoboTwizy

<a href="https://i.gyazo.com/702abd99879359948dfb4e1742a99815.png"><img src="https://i.gyazo.com/702abd99879359948dfb4e1742a99815.png" alt="Image from Gyazo" width="200"/></a>

View the [Wiki](https://robowiki.twizy.dev/)

## Description

RoboTwizy: A mystical Discord companion, weaving enchanting wisdom and magic into your servers for a magical experience

![Badge](https://api.checklyhq.com/v1/badges/checks/96e08efd-4a4a-41af-b2d2-2baf2c3eed3c?style=flat&theme=default)

## Installation

Create an `.env` file in the root directory with the following variables:

```bash
DISCORD_TOKEN=
POSTGRES_URL=
GUILD_ID=
GENERAL_CHANNEL_ID=
BOT_CHANNEL_ID=
AWS_ACCESS_KEY=
AWS_SECRET_ACCESS_KEY=
PREFIX=
LAVALINK_URI=
LAVALINK_PASSWORD=
HEALTHCHECK_URL=
X-API-KEY=
```

Run the bot:

```bash
./run.sh
```

## Notes

The Bot is hosted on [Railway](https://railway.app/). I have plans to set this up using terraform, but for now, it's a manual process.
