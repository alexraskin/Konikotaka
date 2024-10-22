# Konikotaka

Konikotaka is a Discord Bot that I created for my personal server. It's a fun project that I use to learn new technologies and concepts.

<a href="https://i.gyazo.com/12ccb49e7c6b2e31a207ad63e38e7f36.png"><img src="https://i.gyazo.com/12ccb49e7c6b2e31a207ad63e38e7f36.png" alt="Konikotaka" width="200"/></a>

_Name and Photo [Konikotaka](https://youtu.be/Qr2LQILdXD0?si=WwoM0emUIa_8dBfJ)_

## Features

- Moderation
- Fun
- Utility
- Games
- [OpenAI](https://openai.com/)
- [Cloudflare AI](https://ai.cloudflare.com/)
- Anime Waifus (SFW)
- Memes (SFW)

## Running the Bot Locally

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
HEALTHCHECK_URL=
X-API-KEY=
CLIENT_ID=
OPENAI_TOKEN=
CLOUDFLARE_AI_GATEWAY_URL=
CLOUDFLARE_AI_URL=
CLOUDFLARE_AI_TOKEN=
```

Build the docker image:

```bash
docker build -t konikotaka .
```

```bash
docker run --env-file ./.env -p 8000:8000 konikotaka
```

or pull the docker image:

```bash
docker pull ghcr.io/alexraskin/konikotaka:latest
```

## Contributing

I prefer if you don't contribute to this project. It's a personal project that I use to learn new technologies and concepts. If you have any suggestions, please open an issue.

## Privacy Policy and Terms of Service

No personal data is stored.

## License

[MPL 2.0](https://choosealicense.com/licenses/mpl-2.0/)
