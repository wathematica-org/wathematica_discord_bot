import config
import discord
import utility_methods as ut
from discord.commands import slash_command
from discord.ext import commands


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

        # this command require the user to have manage_channel permission
        if not ctx.author.guild_permissions.manage_channels:
            embed = discord.Embed(
                title="<:x:960095353577807883> ゼミ終了処理失敗",
                description="当該操作に必要な権限が不足しています。",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return

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

        # delete the message in role_settings channel
        role_channel = await ut.get_text_channel_by_channel_name(
            scope=ctx.guild, channel_name=config.channel_names["role_settings"]
        )
        async for message in role_channel.history(limit=300):
            if message.author.name != config.bot_name:
                continue

            embed_objects_in_the_message: list[discord.Embed] = message.embeds
            if not embed_objects_in_the_message:
                # messages from old bot does not have embed object.
                continue

            # each message in role_settings channel has only one embed object
            embed_object_in_the_message = embed_objects_in_the_message[0]
            seminar_name_in_the_message = embed_object_in_the_message.title

            if seminar_name_in_the_message == seminar_name:
                await message.delete()
                break

        embed = discord.Embed(
            title="<:white_check_mark:960095096563466250> ロール付与メッセージ削除成功",
            description=f"{role_channel.mention} のロール付与メッセージを削除しました。",
            color=discord.Colour.brand_green(),
        )
        await ctx.respond(embed=embed)


def setup(bot: discord.Bot):
    bot.add_cog(End(bot))
