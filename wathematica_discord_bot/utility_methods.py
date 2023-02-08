from typing import Optional

import discord


async def get_category_by_category_name(
    guild: discord.Guild, category_name: str
) -> Optional[discord.CategoryChannel]:
    """
    retrieve discord.CategoryChannel object with the specified name

    Parameters
    ----------
    guild: discord.Guild
        the guild to search for category_name in.
    category_name: str
        category name to search for.

    Returns
    ----------
    category: Optional[discord.CategoryChannel]
        the desired category if there's a category whose name is category_name.
    """
    for category in guild.categories:
        if category.name == category_name:
            return category


async def get_text_channel_by_channel_name(
    scope: discord.CategoryChannel | discord.Guild, channel_name: str
) -> Optional[discord.TextChannel]:
    """
    retrieve discord.TextChannel object with the specified name

    Parameters
    ----------
    scope: Union[discord.CategoryChannel, discord.Guild]
        the scope to search for channel_name within. (e.g. ctx.guild)
    channel_name: str
        name of the text channel to search for.

    Returns
    ----------
    channel: Optional[discord.TextChannel]
        the desired channel if there's a text channel whose name is channel_name.
    """
    for channel in scope.text_channels:
        if channel.name == channel_name:
            return channel


async def get_role_by_role_name(
    guild: discord.Guild, role_name: str
) -> Optional[discord.Role]:
    """
    retrieve discord.Role object with the specified name

    Parameters
    ----------
    guild: discord.Guild
        the guild to search for role_name in.
    role_name: str
        name of the role to search for.

    Returns
    ----------
    role: Optional[discord.Role]
        the desired role if there's a role whose name is role_name.
    """
    for role in guild.roles:
        if role.name == role_name:
            return role


async def delete_message_with_message_id(message_id: int):
    """
    delete a message whose id is message_id.

    Parameters
    ----------
    message_id: int
        id of the message to be deleted
    """
    # TODO: Implement a function to retrieve message object from message id.
    # Be careful that a message object could be None.
