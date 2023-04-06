import discord
from discord.ext import commands
from exceptions import InvalidCategoryException, InvalidChannelTypeException


def specific_categories_only(category_ids: list[int]):
    """
    Parameters:
        category_ids: list[int]
            IDs of categories where this command can be executed.
    Returns:
        _ : bool
            whether the category where this command was executed matched any of category_ids.
    Raises:
        InvalidCategoryException
            raised when the category where this command was executed matched none of category_ids.
    """

    async def predicate(ctx: discord.ApplicationContext) -> bool:
        if ctx.channel.category_id in category_ids:
            return True
        else:
            raise InvalidCategoryException(
                "Command was executed in an invalid category"
            )

    return commands.check(predicate)


def textchannel_only():
    """
    Returns:
        _ : bool
            whether the channel where this command was executed is a "pure" text channel, not a thread.
    Raises:
        InvalidChannelTypeException
            raised when the channel where this command was executed is not a "pure" text channel.
    """

    async def predicate(ctx: discord.ApplicationContext) -> bool:
        if isinstance(ctx.channel, discord.TextChannel):
            return True
        else:
            raise InvalidChannelTypeException(
                "Command was executed in an invalid channel"
            )

    return commands.check(predicate)
