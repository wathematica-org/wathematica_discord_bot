import config
import discord
from discord import Option
from discord.commands import slash_command
from discord.ext import commands


class Reload(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @slash_command(
        name="reload",
        description="[技術部専用] 指定されたCogをリロードします",
        guild_ids=config.guilds,
    )
    # 822094687548342292 is the id of '技術部' role
    # see https://docs.pycord.dev/en/master/ext/commands/api.html#checks to know how to use 'checker' decorators like 'has_role'
    @commands.has_role(822094687548342292)
    async def reload(
        self,
        ctx: discord.ApplicationContext,
        cog_specifier: Option(input_type=str, description="リロードしたいCog名", required=True),  # type: ignore
    ):
        # reload specified cog
        # cog_specifier will be like "Cogs.AdminTools.reload"
        self.bot.reload_extension(cog_specifier)
        embed = discord.Embed(
            title="<:arrows_counterclockwise:960172711924088882> Cogリロード成功",
            description=f"Cog `{cog_specifier}` をリロードしました。",
            color=discord.Colour.brand_green(),
        )
        await ctx.respond(embed=embed)

    @reload.error
    async def reload_error(
        self, error: commands.CheckFailure, ctx: discord.ApplicationContext
    ):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                title="<:x:960095353577807883> Cogリロード失敗",
                description="当該操作には技術部ロールが必要です。",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
        else:
            raise Exception("Unexpected error occurred in reload.")


def setup(bot: discord.Bot):
    bot.add_cog(Reload(bot))
