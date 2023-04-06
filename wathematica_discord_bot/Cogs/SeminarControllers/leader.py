import config
import discord
from checks import specific_categories_only, textchannel_only
from database import async_session
from discord.commands import slash_command
from discord.ext import commands
from exceptions import InvalidCategoryException, InvalidChannelTypeException
from model import Seminar
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound


class Leader(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.guild_only()
    @specific_categories_only(
        category_ids=[
            config.category_info["pending_seminars"]["id"],
            config.category_info["ongoing_seminars"]["id"],
        ]
    )
    @textchannel_only()
    @slash_command(
        name="leader",
        description="このゼミのゼミ長を表示します",
        guild_ids=config.guilds,
    )
    async def leader(self, ctx: discord.ApplicationContext):
        # [ give additional information to type checker
        # guild_only() decorator ensures that ctx.guild is not None
        assert isinstance(ctx.guild, discord.Guild)
        # In guild, ctx.channel is always a TextChannel or Thread
        assert isinstance(ctx.channel, discord.TextChannel) or isinstance(
            ctx.channel, discord.Thread
        )
        # ]

        async with async_session() as session:
            async with session.begin():
                try:
                    this_seminar: Seminar = (
                        await session.execute(
                            select(Seminar).where(
                                Seminar.channel_id == ctx.channel.id,
                                Seminar.server_id == ctx.guild_id,
                            )
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

    @leader.error
    async def leader_error(
        self, ctx: discord.ApplicationContext, error: commands.CheckFailure
    ):
        if isinstance(error, InvalidChannelTypeException):
            embed = discord.Embed(
                title="<:x:960095353577807883> 不正な操作です",
                description="このコマンドはスレッド内では実行できません。",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return
        if isinstance(error, InvalidCategoryException):
            embed = discord.Embed(
                title="<:x:960095353577807883> 不正な操作です",
                description=f'{config.category_info["pending_seminars"]["name"]}または{config.category_info["ongoing_seminars"]["name"]}にあるテキストチャンネルでのみ実行可能です。',
                color=discord.Colour.red(),
            )
            await ctx.respond(
                embed=embed, delete_after=config.display_time_of_trivial_error
            )
            return

        raise Exception("Unexpected error occurred.")


def setup(bot: discord.Bot):
    bot.add_cog(Leader(bot))
