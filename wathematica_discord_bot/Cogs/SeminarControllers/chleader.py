import textwrap

import config
import discord
from checks import specific_categories_only, textchannel_only
from discord import Option
from discord.commands import slash_command
from discord.ext import commands
from exceptions import InvalidCategoryException, InvalidChannelTypeException
from model import Seminar
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from app import WathematicaBot


class ChangeLeader(commands.Cog):
    def __init__(self, bot: WathematicaBot):
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
        name="chleader",
        description="このゼミのゼミ長を変更します",
        guild_ids=[config.guild_id],
    )
    async def chleader(
        self,
        ctx: discord.ApplicationContext,
        new_leader_name: Option(
            input_type=str, description="新ゼミ長のユーザ指定名", required=True
        ),  # type: ignore
    ):
        # [ give additional information to type checker
        assert isinstance(new_leader_name, str)
        # guild_only() decorator ensures that ctx.guild is not None
        assert isinstance(ctx.guild, discord.Guild)
        # In guild, ctx.channel is always a TextChannel or Thread
        assert isinstance(ctx.channel, discord.TextChannel) or isinstance(
            ctx.channel, discord.Thread
        )
        # In guild, ctx.author is always a Member
        assert isinstance(ctx.author, discord.Member)
        # ]

        # when the user is mistakenly mentioned in the argument of this command,
        # `new_leader_name` will be like "<@123456789012345678>"
        if new_leader_name.startswith("<@"):
            embed = discord.Embed(
                title="<:x:960095353577807883> ユーザIDを正しく指定してください",
                description=textwrap.dedent(
                    f"""
                    ユーザをメンションするのではなく、IDを指定してください。
                    例えばあなたのIDは `{ctx.author.name}` です。
                    """
                ),
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return

        new_leader = ctx.guild.get_member_named(new_leader_name)
        if not new_leader:
            embed = discord.Embed(
                title="<:x:960095353577807883> ユーザが存在しません",
                description=f"`{new_leader_name}` というユーザは存在しません。",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return

        # check if the user who executed this command has permission to change the leader
        async with self.bot.db.create_session() as session:
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
                    current_leader_id = this_seminar.leader_id
                except NoResultFound:
                    embed = discord.Embed(
                        title="<:x:960095353577807883> データベース検索失敗",
                        description="このゼミはデータベースに存在しません。",
                        color=discord.Colour.red(),
                    )
                    await ctx.respond(embed=embed)
                    return

                # check if the author is the current leader or has manage_channels permission
                if not (
                    current_leader_id == ctx.author.id
                    or ctx.author.guild_permissions.manage_channels
                ):
                    embed = discord.Embed(
                        title="<:x:960095353577807883> ゼミ長変更処理失敗",
                        description="現在のゼミ長のみがゼミ長を変更できます。",
                        color=discord.Colour.red(),
                    )
                    await ctx.respond(embed=embed)
                    return

                # update the leader of this seminar in database
                this_seminar.leader_id = new_leader.id

        embed = discord.Embed(
            title="<:white_check_mark:960095096563466250> ゼミ長更新成功",
            description=f"このゼミのゼミ長が {new_leader.mention} になりました。",
            color=discord.Colour.brand_green(),
        )
        await ctx.respond(embed=embed)

    @chleader.error
    async def chleader_error(
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
    bot.add_cog(ChangeLeader(bot))
