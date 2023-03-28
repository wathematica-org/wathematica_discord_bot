import textwrap

import config
import discord
from database import async_session
from discord import Option
from discord.commands import slash_command
from discord.ext import commands
from model import Seminar
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound


class ChangeLeader(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.guild_only()
    @slash_command(
        name="chleader",
        description="このゼミのゼミ長を変更します",
        guild_ids=config.guilds,
    )
    async def chleader(
        self,
        ctx: discord.ApplicationContext,
        new_leader_name: Option(input_type=str, description="新ゼミ長のユーザ指定名", required=True),  # type: ignore
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

        if ctx.channel.category is None or ctx.channel.category.id not in (
            config.category_info["pending_seminars"]["id"],
            config.category_info["ongoing_seminars"]["id"],
        ):
            embed = discord.Embed(
                title="<:x:960095353577807883> 不正な操作です",
                description=f'{config.category_info["ongoing_seminars"]["name"]}または{config.category_info["pending_seminars"]["name"]}にあるテキストチャンネルでのみ実行可能です。',
                color=discord.Colour.red(),
            )
            await ctx.respond(
                embed=embed, delete_after=config.display_time_of_trivial_error
            )
            return

        # when the user is mistakenly mentioned in the argument of this command,
        # `new_leader_name` will be like "<@123456789012345678>"
        if new_leader_name.startswith("<@") or "#" not in new_leader_name:
            embed = discord.Embed(
                title="<:x:960095353577807883> ユーザ名を正しく指定してください",
                description=textwrap.dedent(
                    f"""
                    ユーザ指定名は `ユーザ名#4桁の数字` の形をしています。
                    ユーザ指定名はメンション記号の@を含まず、#の前後にスペースを含みません。
                    例えばあなたの場合は `{ctx.author.name}#{ctx.author.discriminator}` です。
                    ユーザ指定名を確認する方法は以下のリンクを参照してください。
                    https://discord2.tokyo/archives/1177#outline__1
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
        async with async_session() as session:
            async with session.begin():
                try:
                    this_seminar: Seminar = (
                        await session.execute(
                            select(Seminar).where(Seminar.channel_id == ctx.channel.id)
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


def setup(bot: discord.Bot):
    bot.add_cog(ChangeLeader(bot))
