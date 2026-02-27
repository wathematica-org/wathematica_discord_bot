import discord
from discord.ext import commands
from discord.commands import slash_command

from view.settings_view import get_settings_embed, SettingsDashboardView


class Settings(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @slash_command(
        name="setting",
        description="サーバー設定ダッシュボードを開きます",
        default_member_permissions=discord.Permissions(administrator=True),
    )
    async def guild_setting(self, ctx: discord.ApplicationContext):
        await ctx.defer()

        # 1. UIファイルから最新の Embed を生成してもらう
        embed = await get_settings_embed(ctx.guild.id, ctx.guild.name, self.bot)

        # 2. UIファイルからボタン群 (View) を生成する
        view = SettingsDashboardView(self.bot)

        # 3. メッセージを送信！
        await ctx.respond(embed=embed, view=view)


def setup(bot: discord.Bot):
    bot.add_cog(Settings(bot))
