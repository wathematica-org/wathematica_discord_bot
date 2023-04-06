import config
import discord
from discord import ExtensionNotFound, ExtensionNotLoaded, Option
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
    # see https://docs.pycord.dev/en/master/ext/commands/api.html#checks to
    # know how to use 'checker' decorators like 'has_role'
    @commands.has_role(config.engineer_role_id)
    async def reload(
        self,
        ctx: discord.ApplicationContext,
        cog_specifier: Option(input_type=str, description="リロードしたいCog名", required=True),  # type: ignore
    ):
        # reload specified cog
        # cog_specifier will be like "Cogs.AdminTools.reload"
        try:
            self.bot.reload_extension(cog_specifier)
        except (ExtensionNotLoaded, ExtensionNotFound):
            embed = discord.Embed(
                title="<:x:960095353577807883> Cogリロード失敗",
                description=f"Cog `{cog_specifier}` が見つかりませんでした。",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title="<:arrows_counterclockwise:960172711924088882> Cogリロード成功",
                description=f"Cog `{cog_specifier}` をリロードしました。",
                color=discord.Colour.brand_green(),
            )
            await ctx.respond(embed=embed)

    @reload.error
    async def reload_error(
        self, ctx: discord.ApplicationContext, error: commands.CheckFailure
    ):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                title="<:x:960095353577807883> Cogリロード失敗",
                description="当該操作には技術部ロールが必要です。",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return

        raise Exception("Unexpected error occurred in reload.")


def setup(bot: discord.Bot):
    bot.add_cog(Reload(bot))
