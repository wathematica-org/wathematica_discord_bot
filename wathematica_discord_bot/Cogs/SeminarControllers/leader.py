import config
import discord
from database import async_session
from discord.commands import slash_command
from discord.ext import commands
from model import Seminar
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound


class Leader(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.guild_only()
    @slash_command(
        name="leader",
        description="このゼミのゼミ長を表示します",
        guild_ids=config.guilds,
    )
    async def leader(self, ctx: discord.ApplicationContext):

        # ignore if the channel in which this command is called is not in either ongoing_seminars or pending_seminars
        if ctx.channel.category.name not in (
            config.category_names["ongoing_seminars"],
            config.category_names["pending_seminars"],
        ):
            embed = discord.Embed(
                title="<:x:960095353577807883> 不正な操作です",
                description=f'{config.category_names["ongoing_seminars"]}または{config.category_names["pending_seminars"]}にあるテキストチャンネルでのみ実行可能です。',
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return

        async with async_session() as session:
            async with session.begin():
                try:
                    this_seminar: Seminar = (
                        await session.execute(
                            select(Seminar).where(Seminar.channel_id == ctx.channel.id)
                        )
                    ).scalar_one()
                    leader_id = this_seminar.leader_id
                except NoResultFound:
                    embed = discord.Embed(
                        title="<:x:960095353577807883> データベース検索失敗",
                        description="このゼミはデータベースに存在しません。",
                        color=discord.Colour.red(),
                    )
                    await ctx.respond(embed=embed)
                    return

        leader = ctx.guild.get_member(leader_id)
        if not leader:
            embed = discord.Embed(
                title="<:x:960095353577807883> ゼミ長情報取得失敗",
                description="ゼミ長はこのサーバーに参加していません。",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return

        embed = discord.Embed(
            title="<:information_source:1072876408579293185> ゼミ長情報取得成功",
            description=f"このゼミのゼミ長は `{leader.display_name}` です。",
            color=discord.Colour.brand_green(),
        )
        await ctx.respond(embed=embed)


def setup(bot: discord.Bot):
    bot.add_cog(Leader(bot))
