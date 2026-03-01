import discord
from checks import specific_states_only, textchannel_only, registered_server_only
from database import async_session
from discord.commands import slash_command
from discord.ext import commands
from exceptions import *
from model import Seminar, SeminarState, Category
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
import utils


class Pause(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.guild_only()
    @registered_server_only()
    @specific_states_only(states=[SeminarState.ONGOING])
    @textchannel_only()
    @slash_command(
        name="pause",
        description="ゼミを《ゼミ(本運用)》から《ゼミ(休止中)》に移動させます",
    )
    async def pause(self, ctx: discord.ApplicationContext):
        # [ give additional information to type checker
        # guild_only() decorator ensures that ctx.guild is not None
        assert isinstance(ctx.guild, discord.Guild)
        # ]

        paused_seminar_category = await utils.get_category(ctx, SeminarState.PAUSED)
        if not isinstance(paused_seminar_category, discord.CategoryChannel):
            embed = discord.Embed(
                title="<:x:960095353577807883> システムエラー",
                description="管理者向けメッセージ: `paused_seminars` カテゴリが見つかりませんでした。",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return

        # move the channel to the paused_seminar category
        await ctx.channel.edit(
            category=paused_seminar_category, reason=f"Requested by {ctx.author.name}"
        )

        async with async_session() as session:
            async with session.begin():
                try:
                    this_seminar: Seminar = (
                        await session.execute(
                            select(Seminar)
                            .join(Category)
                            .where(
                                Seminar.channel_id == ctx.channel.id,
                                Category.guild_id == ctx.guild_id,
                            )
                        )
                    ).scalar_one()
                    this_seminar.category_id = paused_seminar_category.id
                except NoResultFound:
                    embed = discord.Embed(
                        title="<:warning:960146803846684692> データベース編集失敗",
                        description="このゼミはデータベースに存在しません。",
                        color=discord.Colour.yellow(),
                    )
                    await ctx.respond(embed=embed)

        embed = discord.Embed(
            title="<:white_check_mark:960095096563466250> チャンネル移動成功",
            description=f"チャンネルを《{paused_seminar_category.name}》へ移動しました。",
            color=discord.Colour.brand_green(),
        )
        await ctx.respond(embed=embed)

    @pause.error
    async def pause_error(
        self, ctx: discord.ApplicationContext, error: commands.CheckFailure
    ):
        if isinstance(error, ConfigurationNotCompleteException):
            embed = discord.Embed(
                title="<:x:960095353577807883> サーバー設定ができていません",
                description="管理者に `/setting` で設定を依頼してください。",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return
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
                description="《ゼミ(本運用)》にあるテキストチャンネルでのみ実行可能です。",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return
        if isinstance(error, CategoryNotRegisteredException):
            embed = discord.Embed(
                title=":x: チャンネル作成失敗",
                description="《ゼミ(休止中)》カテゴリーが登録されていません。管理者に `/setting` で設定を依頼してください。",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return
        if isinstance(error, CategoryUnavailableException):
            embed = discord.Embed(
                title=":x: チャンネル作成失敗",
                description="《ゼミ(休止中)》カテゴリーに空きがありません。管理者にカテゴリー作成・設定を依頼してください。",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return

        raise Exception("Unexpected error occurred.")


def setup(bot: discord.Bot):
    bot.add_cog(Pause(bot))
