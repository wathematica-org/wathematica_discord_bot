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
        "id": 1080865149902131270,
        "name": "全般",
    },
    "pending_seminars": {
        "id": 1089089108120457278,
        "name": "ゼミ(仮立て)",
    },
    "ongoing_seminars": {
        "id": 1089089162461855804,
        "name": "ゼミ(本運用)",
    },
    "paused_seminars": {
        "id": 1089089754483654687,
        "name": "ゼミ(休止中)",
    },
    "finished_seminars": {
        "id": 1089089785362120744,
        "name": "ゼミ(終了)",
    },
}
channel_info: dict[str, ChannelInfo] = {
    "role_settings": {
        "id": 1093502316147118140,
        "name": "権限設定",
    },
}
# display error message for 30 seconds if the error is trivial
display_time_of_trivial_error: int = 30

# Discord server-specific settings
guild_id: int = 1080865149436571688
engineer_role_id: int = 1089104583642579055
interesting_emoji_id: int = 1093517491470352467
