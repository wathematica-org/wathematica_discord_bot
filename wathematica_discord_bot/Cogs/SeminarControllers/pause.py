import config
import discord
from checks import specific_categories_only, textchannel_only
from discord.commands import slash_command
from discord.ext import commands
from exceptions import InvalidCategoryException, InvalidChannelTypeException
from model import Seminar, SeminarState
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from app import WathematicaBot


class Pause(commands.Cog):
    def __init__(self, bot: WathematicaBot):
        self.bot = bot

    @commands.guild_only()
    @specific_categories_only(
        category_ids=[
            config.category_info["ongoing_seminars"]["id"],
        ]
    )
    @textchannel_only()
    @slash_command(
        name="pause",
        description=f'ゼミを{config.category_info["ongoing_seminars"]["name"]}から{config.category_info["paused_seminars"]["name"]}に移動させます',
        guild_ids=[config.guild_id],
    )
    async def pause(self, ctx: discord.ApplicationContext):
        # [ give additional information to type checker
        # guild_only() decorator ensures that ctx.guild is not None
        assert isinstance(ctx.guild, discord.Guild)
        # ]

        paused_seminar_category = ctx.guild.get_channel(
            config.category_info["paused_seminars"]["id"]
        )
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
                    this_seminar.seminar_state = SeminarState.PAUSED
                except NoResultFound:
                    embed = discord.Embed(
                        title="<:warning:960146803846684692> データベース編集失敗",
                        description="このゼミはデータベースに存在しません。",
                        color=discord.Colour.yellow(),
                    )
                    await ctx.respond(embed=embed)

        embed = discord.Embed(
            title="<:white_check_mark:960095096563466250> チャンネル移動成功",
            description=f'チャンネルを{config.category_info["paused_seminars"]["name"]}へ移動しました。',
            color=discord.Colour.brand_green(),
        )
        await ctx.respond(embed=embed)

    @pause.error
    async def pause_error(
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
                description=f'{config.category_info["ongoing_seminars"]["name"]}にあるテキストチャンネルでのみ実行可能です。',
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return

        raise Exception("Unexpected error occurred.")


def setup(bot: discord.Bot):
    bot.add_cog(Pause(bot))
