import glob

from discord.ext import commands


class AdminTools(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        cog_filenames: list[str] = glob.glob(
            "Cogs/AdminTools/[a-zA-Z]*.py"
        )  # exclude __init__.py
        cogs = list(
            map(lambda x: x.replace("/", ".").replace(".py", ""), cog_filenames)
        )
        for cog in cogs:
            self.bot.load_extension(cog)


def setup(bot: commands.Bot):
    bot.add_cog(AdminTools(bot))
