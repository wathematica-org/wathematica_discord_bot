import config
import discord
import utility_methods as ut
from discord.ext import commands


class RoleAssigner(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        member = payload.member
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        # ignore reactions from bot
        if member.bot:
            return
        # ignore reactions that happens in channels other than role_setting channel
        # or belongs to other user's message
        # TODO: Implement error handling to prevent this event from being triggered in DM
        if (
            channel.name != config.channel_names["role_settings"]
            or message.author.name != config.bot_name
        ):
            return
        # react only to "interesting" emoji
        if payload.emoji.id != 836259755302453299:
            return

        embed_objects_in_the_message: list[discord.Embed] = message.embeds
        if not embed_objects_in_the_message:
            # messages from old bot does not have embed object.
            return

        # each message in role_settings channel has only one embed object
        embed_object_in_the_message = embed_objects_in_the_message[0]
        seminar_name = embed_object_in_the_message.title

        seminar_role = await ut.get_role_by_role_name(
            guild=message.guild, role_name=seminar_name
        )
        if not seminar_role:
            embed = discord.Embed(
                title="<:x:960095353577807883> ロール付与失敗",
                description=f"ロール `{seminar_name}` が存在しません。",
                color=discord.Colour.red(),
            )
            await message.channel.send(embed=embed)
        else:
            await member.add_roles(seminar_role)


def setup(bot: discord.Bot):
    bot.add_cog(RoleAssigner(bot))
