import argparse
import config
import os
from typing import Optional


import discord


class WathematicaBot(discord.Bot):
    def __init__(
        self,
        intents: discord.Intents,
        description: Optional[str] = None,
        *args,
        **options,
    ):
        super().__init__(intents=intents, description=description, *args, **options)

    async def on_ready(self):
        if self.user:  # Ensure the bot is logged in
            activity = discord.Activity(
                name="/help でガイドを表示", type=discord.ActivityType.playing
            )
            await self.change_presence(activity=activity)
            print(f"Successfully logged in as {self.user.name}")
        else:
            raise Exception("Failed to log in to Discord server.")


# fEnable type hinting and IntelliSense for parsed arguments
class Args(argparse.Namespace):
    config_file: str


parser = argparse.ArgumentParser(description="Wathematica Discord Bot")
parser.add_argument(
    "--config_file", help="Path to the configuration file", required=True
)

if __name__ == "__main__":
    args = parser.parse_args(namespace=Args())
    # If you don't know what intent is, visit https://docs.pycord.dev/en/stable/intents.html
    intents: discord.Intents = discord.Intents.all()
    intents.typing = False  # Don't react to user's typing event
    intents.presences = False  # Don't react to change of each user's presence

    config.load_json(args.config_file)

    bot = WathematicaBot(intents=intents, description="Wathematicaのゼミを管理します。")
    # Check how to import cogs at https://docs.pycord.dev/en/stable/ext/commands/extensions.html
    # Cogs should be specified as a relative path from the directory where this app.py is located
    bot.load_extension("Cogs.admin_tools")
    bot.load_extension("Cogs.seminar_controllers")
    bot.load_extension("Cogs.user_controllers")
    if os.path.exists("/run/secrets/discord_token"):
        with open("/run/secrets/discord_token") as discord_token_file:
            # Strip the tailing newline character with strip()
            token = discord_token_file.readline().strip()
        # Launch bot
        print(f"{token=}")
        bot.run(token)
    else:
        token = os.environ.get("discord_token")
        if token is None:
            raise FileNotFoundError(
                "[NO TOKEN PROVIDED] check docker-compose.yml to see how you can expose token at /run/secrets/discord_token"
            )
        print("SUCCESS to get token by env.")
        bot.run(token)
