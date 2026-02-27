import discord
from discord.ext import commands
from exceptions import (
    InvalidCategoryException,
    InvalidChannelTypeException,
    ConfigurationNotCompleteException,
    HasEngineerRoleException,
)
from model import SeminarState, Category, Guild
from database import async_session
from sqlalchemy import select


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


def specific_states_only(states: list[SeminarState]):
    """
    Parameters:
        states: list[SeminarState]
            states of categories where this command can be executed.
    Return:
        _ : bool
            whether the category where this command was executed matched any of states.
    Raises:
        InvalidCategoryException
            raised when the category where this command was executed matched none of states.
    """

    async def predicate(ctx: discord.ApplicationContext) -> bool:
        async with async_session() as session:
            category_record = (
                await session.execute(
                    select(Category).where(
                        Category.category_id == ctx.channel.category_id
                    )
                )
            ).scalar_one_or_none()

        if not category_record:
            raise InvalidCategoryException(
                "Command was executed in a category that is not registered in the datebase"
            )

        if category_record.state in states:
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


def registered_server_only():
    """
    Returns:
        _ : bool
            whether the settings was completed
    Raises:
        ConfigurationNotCompleteException
            raised when the settings of the server was not completed.
    """

    async def predicate(ctx: discord.ApplicationContext) -> bool:
        async with async_session() as session:
            guild_record = (
                await session.execute(
                    select(Guild).where(Guild.guild_id == ctx.guild_id)
                )
            ).scalar_one_or_none()
        if not guild_record:
            raise ConfigurationNotCompleteException("Server setting was not completed")

        if all(
            [
                guild_record.interesting_emoji_id,
                guild_record.engineer_role_id,
                guild_record.role_setting_channel_id,
                guild_record.system_channel_id,
            ]
        ):
            return True
        else:
            raise ConfigurationNotCompleteException("Server setting was not completed")

    return commands.check(predicate)


def has_engineer_role_only():
    async def predicate(ctx: discord.ApplicationContext) -> bool:
        async with async_session() as session:
            guild_record = (
                await session.execute(
                    select(Guild).where(Guild.guild_id == ctx.guild_id)
                )
            ).scalar_one_or_none()

        if not guild_record:
            raise ConfigurationNotCompleteException("Server setting was not completed")

        if guild_record.engineer_role_id in ctx.author.roles:
            return True
        else:
            raise HasEngineerRoleException("Command was used by non engineer role user")

    return commands.check(predicate)
