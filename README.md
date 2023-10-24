# Konikotaka

Konikotaka is a Discord Bot that I created for my personal server. It's a fun project that I use to learn new technologies and concepts.

<a href="https://i.gyazo.com/12ccb49e7c6b2e31a207ad63e38e7f36.png"><img src="https://i.gyazo.com/12ccb49e7c6b2e31a207ad63e38e7f36.png" alt="Konikotaka" width="200"/></a>

_Name and Photo [Konikotaka](https://youtu.be/Qr2LQILdXD0)_

## Running

I would prefer if you don't run an instance of my bot. Just call the invite command with an invite URL to have it on your server.

Nevertheless, the installation steps are as follows:

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

This script will activate the virtual environment, install the dependencies, and run the bot.

## Notes

The Bot is hosted on [Railway](https://railway.app/). I have plans to set this up using terraform, but for now, it's a manual process.

## Contributing

I prefer if you don't contribute to this project. It's a personal project that I use to learn new technologies and concepts. If you have any suggestions, please open an issue.

## Privacy Policy and Terms of Service

No personal data is stored.

## License

[MPL 2.0](https://choosealicense.com/licenses/mpl-2.0/)
