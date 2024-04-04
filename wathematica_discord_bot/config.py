from typing import TypedDict


# discord category is recognized as a special type of channel,
# so this object is named "ChannelInfo"
class ChannelInfo(TypedDict):
    id: int
    name: str


# Fundamental settings
bot_name: str = "Wathematica Bot"
category_info: dict[str, ChannelInfo] = {
    "general": {
        "id": 1218953598550020137,
        "name": "全般",
    },
    "pending_seminars": {
        "id": 1218953941245493379,
        "name": "ゼミ(仮立て)",
    },
    "ongoing_seminars": {
        "id": 1218954017980285038,
        "name": "ゼミ(本運用)",
    },
    "paused_seminars": {
        "id": 1218954072359567490,
        "name": "ゼミ(休止中)",
    },
    "finished_seminars": {
        "id": 1218954115519090850,
        "name": "ゼミ(終了)",
    },
}
channel_info: dict[str, ChannelInfo] = {
    "role_settings": {
        "id": 1218953566698471444,
        "name": "権限設定",
    },
}
# display error message for 30 seconds if the error is trivial
display_time_of_trivial_error: int = 30

# Discord server-specific settings
guild_id: int = 1218951406128726207
engineer_role_id: int = 1218956604968534206
interesting_emoji_id: int = 1219276342227505202
