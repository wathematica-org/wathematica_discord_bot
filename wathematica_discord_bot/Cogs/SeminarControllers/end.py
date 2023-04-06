import datetime

import config
import discord
from checks import specific_categories_only, textchannel_only
from database import async_session
from discord.commands import slash_command
from discord.ext import commands
from exceptions import InvalidCategoryException, InvalidChannelTypeException
from model import Seminar, SeminarState
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound


class End(commands.Cog):
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
        name="end",
        description=f'終了したゼミを{config.category_info["finished_seminars"]["name"]}へ移動させ、ロールを削除します。',
        guild_ids=config.guilds,
    )
    async def end(self, ctx: discord.ApplicationContext):
        # [ give additional information to type checker
        # guild_only() decorator ensures that ctx.guild is not None
        assert isinstance(ctx.guild, discord.Guild)
        # In guild, ctx.author is always a Member
        assert isinstance(ctx.author, discord.Member)
        # ]

        # this command must be executed by the leader of the seminar
        # or by someone who has the manage_channels permission
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
                    seminar_name = this_seminar.name
                    current_leader_id = this_seminar.leader_id
                    role_id = this_seminar.role_id
                    role_setting_message_id = this_seminar.role_setting_message_id
                except NoResultFound:
                    embed = discord.Embed(
                        title="<:x:960095353577807883> データベース検索失敗",
                        description="このゼミはデータベースに存在しません。管理者に対応を依頼してください。",
                        color=discord.Colour.red(),
                    )
                    await ctx.respond(embed=embed)
                    return
                else:
                    # Check if there's a text channel with the same name in the finished_seminars category.
                    # Tips: Discord does not allow two channels with the same name in the same category.
                    try:
                        (
                            await session.execute(
                                select(Seminar).where(
                                    Seminar.name == seminar_name,
                                    Seminar.seminar_state == SeminarState.FINISHED,
                                    Seminar.server_id == ctx.guild_id,
                                )
                            )
                        ).scalar_one()
                    except NoResultFound:
                        pass
                    else:
                        embed = discord.Embed(
                            title="<:x:960095353577807883> チャンネル名の重複を検出しました",
                            description=f'すでに同名のゼミが{config.category_info["finished_seminars"]["name"]}に存在します。ゼミ名を `/rename` してから終了してください。',
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
        finished_seminar_category = ctx.guild.get_channel(
            config.category_info["finished_seminars"]["id"]
        )
        if not isinstance(finished_seminar_category, discord.CategoryChannel):
            embed = discord.Embed(
                title="<:x:960095353577807883> システムエラー",
                description="管理者向けメッセージ: `finished_seminars` カテゴリが見つかりませんでした。",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return

        await ctx.channel.edit(
            category=finished_seminar_category, reason=f"Requested by {ctx.author.name}"
        )
        embed = discord.Embed(
            title="<:white_check_mark:960095096563466250> チャンネル移動成功",
            description=f'チャンネルを{config.category_info["finished_seminars"]["name"]}へ移動しました。',
            color=discord.Colour.brand_green(),
        )
        await ctx.respond(embed=embed)

        # delete the role of this seminar
        seminar_role = ctx.guild.get_role(role_id)
        if seminar_role:
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
                        select(Seminar).where(
                            Seminar.channel_id == ctx.channel.id,
                            Seminar.server_id == ctx.guild_id,
                        )
                    )
                ).scalar_one()
                this_seminar.seminar_state = SeminarState.FINISHED
                this_seminar.finished_at = datetime.datetime.now()

        # delete the message in role_settings channel
        role_setting_channel = ctx.guild.get_channel(
            config.channel_info["role_settings"]["id"]
        )
        if not isinstance(role_setting_channel, discord.TextChannel):
            embed = discord.Embed(
                title="<:x:960095353577807883> システムエラー",
                description="管理者向けメッセージ: `role_settings` チャンネルが見つかりませんでした。",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return

        role_setting_message = await role_setting_channel.fetch_message(
            role_setting_message_id
        )
        if role_setting_message:
            await role_setting_message.delete()
            embed = discord.Embed(
                title="<:white_check_mark:960095096563466250> ロール付与メッセージ削除成功",
                description=f"{role_setting_channel.mention} のロール付与メッセージを削除しました。",
                color=discord.Colour.brand_green(),
            )
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title="<:warning:960146803846684692> ロール付与メッセージ削除失敗",
                description=f"{role_setting_channel.mention} にロール付与メッセージが存在しません。",
                color=discord.Colour.yellow(),
            )
            await ctx.respond(embed=embed)

    @end.error
    async def end_error(
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
            await ctx.respond(embed=embed)
            return

        raise Exception("Unexpected error occurred.")


def setup(bot: discord.Bot):
    bot.add_cog(End(bot))
