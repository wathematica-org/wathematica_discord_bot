import json
import os
from typing import TypedDict


# discord category is recognized as a special type of channel,
# so this object is named "ChannelInfo"
class ChannelInfo(TypedDict):
    id: int
    name: str

# Fundamental settings
# FIXME: set bot_name as a discord bot user name
bot_name: str = "Wathematica Bot"
# FIXME: set config_file_path as a path to config file
config_file_path = os.path.join(os.path.dirname(__file__), "config/config-2025.json")

# category_info: dict[str, ChannelInfo]
# channel_info: dict[str, ChannelInfo]
# # display error message for 30 seconds if the error is trivial
# display_time_of_trivial_error: int

# # Discord server-specific settings
# guild_id: int
# engineer_role_id: int
# interesting_emoji_id: int


def load_json() -> None:
    global guild_id, engineer_role_id, interesting_emoji_id
    global display_time_of_trivial_error
    global category_info, channel_info
    file_path = os.path.join(config_file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    server_info = data.get("server-info")
    guild_id = server_info.get("guild_id")
    engineer_role_id = server_info.get("engineer_role_id")
    interesting_emoji_id = server_info.get("interesting_emoji_id",)
    display_time_of_trivial_error = server_info.get(
        "display_time_of_trivial_error", 30
    )
    category_info = data.get("category-info")
    channel_info = data.get("channel-info")
