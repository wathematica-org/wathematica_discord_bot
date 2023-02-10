import datetime

import config
import discord
import utility_methods as ut
from database import async_session
from discord.commands import slash_command
from discord.ext import commands
from model import Seminar, SeminarState
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound


class End(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.guild_only()
    @slash_command(
        name="end",
        description=f'[要編集権限] 終了したゼミを{config.category_names["finished_seminars"]}へ移動させます',
        guild_ids=config.guilds,
    )
    async def end(self, ctx: discord.ApplicationContext):

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

        seminar_name = ctx.channel.name

        # this command must be executed by the leader of the seminar
        # or by someone who has the manage_channels permission
        async with async_session() as session:
            async with session.begin():
                try:
                    this_seminar: Seminar = (
                        await session.execute(
                            select(Seminar).where(Seminar.channel_id == ctx.channel.id)
                        )
                    ).scalar_one()
                    current_leader_id = this_seminar.leader_id
                    role_setting_message_id = this_seminar.role_setting_message_id
                except NoResultFound:
                    embed = discord.Embed(
                        title="<:x:960095353577807883> データベース検索失敗",
                        description="このゼミはデータベースに存在しません。管理者に連絡し手動で対応してもらってください。",
                        color=discord.Colour.red(),
                    )
                    await ctx.respond(embed=embed)
                    return

        if not (
            current_leader_id == ctx.author.id
            or ctx.author.guild_permissions.manage_channels
        ):
            embed = discord.Embed(
                title="<:x:960095353577807883> ゼミ終了処理失敗",
                description="現在のゼミ長のみがゼミを終了できます。",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return

        # move the text channel to the finished_seminars category
        finished_seminar_category = await ut.get_category_by_category_name(
            guild=ctx.guild,
            category_name=config.category_names["finished_seminars"],
        )
        await ctx.channel.edit(
            category=finished_seminar_category, reason=f"Requested by {ctx.author.name}"
        )
        embed = discord.Embed(
            title="<:white_check_mark:960095096563466250> チャンネル移動成功",
            description=f'チャンネルを{config.category_names["finished_seminars"]}へ移動しました。',
            color=discord.Colour.brand_green(),
        )
        await ctx.respond(embed=embed)

        # delete the role of this seminar
        seminar_role = await ut.get_role_by_role_name(
            guild=ctx.guild, role_name=seminar_name
        )
        if seminar_role is not None:
            await seminar_role.delete(reason=f"Requested by {ctx.author.name}")
            embed = discord.Embed(
                title="<:white_check_mark:960095096563466250> ロール削除成功",
                description=f"ロール `{seminar_name}` を削除しました。",
                color=discord.Colour.brand_green(),
            )
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title="<:warning:960146803846684692> ロール削除失敗",
                description=f"ロール `{seminar_name}` は存在しません。",
                color=discord.Colour.yellow(),
            )
            await ctx.respond(embed=embed)

        # mark this seminar as finished in the database
        async with async_session() as session:
            async with session.begin():
                # here, it is ensured that the seminar exists in the database
                this_seminar: Seminar = (
                    await session.execute(
                        select(Seminar).where(Seminar.channel_id == ctx.channel.id)
                    )
                ).scalar_one()
                this_seminar.seminar_state = SeminarState.FINISHED
                this_seminar.finished_at = datetime.datetime.now()

        # delete the message in role_settings channel
        role_channel = await ut.get_text_channel_by_channel_name(
            scope=ctx.guild, channel_name=config.channel_names["role_settings"]
        )
        role_setting_message = await role_channel.fetch_message(
            id=role_setting_message_id
        )
        if role_setting_message:
            role_setting_message.delete()
            embed = discord.Embed(
                title="<:white_check_mark:960095096563466250> ロール付与メッセージ削除成功",
                description=f"{role_channel.mention} のロール付与メッセージを削除しました。",
                color=discord.Colour.brand_green(),
            )
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title="<:warning:960146803846684692> ロール付与メッセージ削除失敗",
                description=f"{role_channel.mention} にロール付与メッセージが存在しません。",
                color=discord.Colour.yellow(),
            )
            await ctx.respond(embed=embed)


def setup(bot: discord.Bot):
    bot.add_cog(End(bot))
