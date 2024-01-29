from rcon import Console
from typing import Optional, Union


class RconClient:
    def __init__(
        self, host: str, password: str, port: int, timeout: Optional[int] = 5
    ) -> None:
        self.host: str = host
        self.password: str = password
        self.port: int = port
        self.timeout: int = timeout

    def open(self) -> Console:
        return Console(
            host=self.host, password=self.password, port=self.port, timeout=5
        )

    # Admin Commands:
    def info(self) -> Union[str, bool]:
        console = self.open()
        res = console.command("Info")
        console.close()
        return res if res else False

    def save(self) -> Union[str, bool]:
        console = self.open()
        res = console.command("Save")
        console.close()
        return res if res else False

    def online(self) -> Union[list, str, bool]:
        # Response is of format `name,playerid,steamid`
        console = self.open()
        res = console.command("ShowPlayers")
        console.close()

        players = []
        # format output
        if res:
            lines = res.split()[1:]
            buffer = ["## List of connected player names"]
            for line in lines:
                words = line.split(",")
                name = words[0]
                steam_id = words[2]
                players.append((name, steam_id))
                buffer.append(f"- {words[0]} (Steam ID: {words[2]})")
            output = "\n".join(buffer)
            return output, players
        else:
            return False, False

    def announce(self, message: str) -> Union[str, bool]:
        console = self.open()
        res = console.command(f"Broadcast {message}")
        console.close()
        # TODO: Consider reformatting server's response
        return res if res else False

    def kick(self, steam_id: str) -> Union[str, bool]:
        console = self.open()
        res = console.command(f"KickPlayer {steam_id}")
        console.close()
        return res if res else False

    def ban(self, steam_id: str) -> Union[str, bool]:
        console = self.open()
        res = console.command(f"BanPlayer {steam_id}")
        console.close()
        return res if res else False

    def shutdown(self, seconds: str, message: str) -> Union[str, bool]:
        console = self.open()
        res = console.command(f"Shutdown {seconds} {message}")
        console.close()
        return res if res else False

    def force_stop(self) -> Union[str, bool]:
        console = self.open()
        res = console.command(f"DoExit")
        console.close()
        # TODO: Check if this is supposed to give a response (and alter accordingly)
        return res if res else False
