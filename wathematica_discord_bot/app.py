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
                name="コマンド受付中", type=discord.ActivityType.playing
            )
            await self.change_presence(activity=activity)
            print(f"Successfully logged in as {self.user.name}")
        else:
            raise Exception("Failed to log in to Discord server.")


if __name__ == "__main__":
    # If you don't know what intent is, visit https://discordpy.readthedocs.io/ja/latest/intents.html
    intents: discord.Intents = discord.Intents.all()
    intents.typing = False  # Don't react to user's typing event
    intents.presences = False  # Don't react to change of each user's presence

    bot = WathematicaBot(intents=intents, description="Wathematicaのゼミを管理します。")
    # Check how to import cogs at https://docs.pycord.dev/en/v2.0.0-beta.1/api.html#discord.Bot.load_extension
    # Cogs should be specified as a relative path from the directory where this app.py is located
    bot.load_extension("Cogs.admin_tools")
    bot.load_extension("Cogs.seminar_controllers")
    bot.load_extension("Cogs.user_controllers")
    if os.path.exists(".credential"):
        with open(".credential") as credential_file:
            # Strip the tailing newline character with strip()
            token = credential_file.readline().strip()
        # Launch bot
        bot.run(token)
    else:
        raise FileNotFoundError(
            "[No credential file was found!] Contact admin and get the .credential file, which contains secret token, "
        )
