import config
import discord
import utility_methods as ut
from discord import Option
from discord.commands import slash_command
from discord.ext import commands


class Delete(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.guild_only()
    @slash_command(
        name="delete",
        description="[要編集権限] 名前が seminar_name のゼミを削除します。",
        guild_ids=config.guilds,
    )
    async def delete(
        self,
        ctx: discord.ApplicationContext,
        seminar_name: Option(input_type=str, description="削除対象のゼミ名", required=True),  # type: ignore
    ):

        # this command require the user to have manage_channel permission
        if not ctx.author.guild_permissions.manage_channels:
            embed = discord.Embed(
                title="<:x:960095353577807883> ゼミ削除処理失敗",
                description="当該操作に必要な権限が不足しています。",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return

        # ignore if this command is called in the exact channel that is to be deleted
        if ctx.channel.name == seminar_name:
            embed = discord.Embed(
                title="<:x:960095353577807883> ゼミ削除処理失敗",
                description="削除対象のチャンネル内からはコマンドを実行できません。",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return

        # keep in mind that ctx.channel and seminar_name are not the same
        seminar_text_channel = await ut.get_text_channel_by_channel_name(
            scope=ctx.guild, channel_name=seminar_name
        )
        if not seminar_text_channel:
            embed = discord.Embed(
                title="<:x:960095353577807883> ゼミ削除失敗",
                description=f"`{seminar_name}` という名前のゼミは存在しません。",
                color=discord.Colour.red(),
            )
            await ctx.respond(embed=embed)
            return

        # delete the text channel
        await seminar_text_channel.delete(reason=f"Requested by {ctx.author.name}")
        embed = discord.Embed(
            title="<:white_check_mark:960095096563466250> チャンネル削除成功",
            description=f"チャンネル `{seminar_name}` を削除しました。",
            color=discord.Colour.brand_green(),
        )
        await ctx.respond(embed=embed)

        # delete the role
        role = await ut.get_role_by_role_name(guild=ctx.guild, role_name=seminar_name)
        if not role:
            embed = discord.Embed(
                title="<:warning:960146803846684692> ロール削除失敗",
                description=f"`{seminar_name}` という名前のロールは存在しません。",
                color=discord.Colour.yellow(),
            )
            await ctx.respond(embed=embed)
            return

        await role.delete(reason=f"Requested by {ctx.author.name}")
        embed = discord.Embed(
            title="<:white_check_mark:960095096563466250> ロール削除成功",
            description=f"ロール `{seminar_name}` を削除しました。",
            color=discord.Colour.brand_green(),
        )
        await ctx.respond(embed=embed)

        # delete the message that is already sent to role_settings channel
        # TODO: This very often doesn't delete message correctly. Fix it!
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
    bot.add_cog(Delete(bot))
