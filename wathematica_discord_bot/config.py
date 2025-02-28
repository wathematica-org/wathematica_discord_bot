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
        "id": 1344929498272890900,
        "name": "全般",
    },
    "pending_seminars": {
        "id": 1344916636733280298,
        "name": "ゼミ(仮立て)",
    },
    "ongoing_seminars": {
        "id": 1344916551559548999,
        "name": "ゼミ(本運用)",
    },
    "paused_seminars": {
        "id": 1344928978007359511,
        "name": "ゼミ(休止中)",
    },
    "finished_seminars": {
        "id": 1344928854891958373,
        "name": "ゼミ(終了)",
    },
}
channel_info: dict[str, ChannelInfo] = {
    "role_settings": {
        "id": 1344917795066085436,
        "name": "権限設定",
    },
}
# display error message for 30 seconds if the error is trivial
display_time_of_trivial_error: int = 30

# Discord server-specific settings
guild_id: int = 1326841905702633484
engineer_role_id: int = 1344931018481598485
interesting_emoji_id: int = 1344930443052711966
