from typing import Literal

import other.Logger as Logger
import discord
import discord.abc
import Bot

TYPE_DM      = 1
TYPE_CHANNEL = 2
CHANNEL_GFAD_SEARCH           = 1
CHANNEL_CARD_REVIEWS          = 2
CHANNEL_ERRORS                = 3
CHANNEL_GOD_CHANNEL           = 4
CHANNEL_REPEAT_LOG            = 5
CHANNEL_SUGGESTIONS           = 6

channel_literal = Literal[
    "CHANNEL_GFAD_SEARCH", "CHANNEL_CARD_REVIEWS",
    "CHANNEL_ERRORS", "CHANNEL_GOD_CHANNEL",
    "CHANNEL_REPEAT_LOG", "CHANNEL_SUGGESTIONS"
]
type_literal       = Literal["TYPE_DM", "TYPE_CHANNEL"]

channel_tree = {
    CHANNEL_GFAD_SEARCH: {
        "name": "CHANNEL_GFAD_SEARCH",
        "id": CHANNEL_GFAD_SEARCH,
        "max": -1,
        "dm": [],
        "channel": [],
    },
    CHANNEL_CARD_REVIEWS: {
        "name": "CHANNEL_CARD_REVIEWS",
        "id": CHANNEL_CARD_REVIEWS,
        "max": 1,
        "dm": [],
        "channel": [],
    },
    CHANNEL_ERRORS: {
        "name": "CHANNEL_ERRORS",
        "id": CHANNEL_ERRORS,
        "max": 1,
        "dm": [],
        "channel": [],
    },
    CHANNEL_GOD_CHANNEL: {
        "name": "CHANNEL_GOD_CHANNEL",
        "id": CHANNEL_GOD_CHANNEL,
        "max": 1,
        "dm": [],
        "channel": [],
    },
    CHANNEL_REPEAT_LOG: {
        "name": "CHANNEL_REPEAT_LOG",
        "id": CHANNEL_REPEAT_LOG,
        "max": 1,
        "dm": [],
        "channel": [],
    },
    CHANNEL_SUGGESTIONS: {
        "name": "CHANNEL_SUGGESTIONS",
        "id": CHANNEL_SUGGESTIONS,
        "max": 1,
        "dm": [],
        "channel": [],
    }
}

channel_settings = Bot.Deweybase.read_data(statement=Bot.Deweybase.create_read_statement(table="channels", values=["id","channeltype","type"]))

def get_channels(channeltype:int, filtertype:int | None = None) -> list[tuple[int,int]]:
    channels = []
    if filtertype == TYPE_DM or filtertype == None:
        for i in channel_tree[channeltype]["dm"]:
            channels.append((TYPE_DM,i))
    if filtertype == TYPE_CHANNEL or filtertype == None:
        for i in channel_tree[channeltype]["channel"]:
            channels.append((TYPE_CHANNEL,i))

    return channels


async def get_channel(channel_def: tuple[int, int]) ->  discord.abc.GuildChannel | discord.abc.PrivateChannel | discord.Thread | discord.TextChannel | discord.DMChannel | None:
    if channel_def[0] == TYPE_DM:
        user = Bot.client.get_user(channel_def[1])
        if not user: 
            user = await Bot.client.fetch_user(channel_def[1])

        if not user.dm_channel: 
            await user.create_dm()

        return user.dm_channel
    elif channel_def[0] == TYPE_CHANNEL:
        channel = Bot.client.get_channel(channel_def[1])
        if not channel:
            channel = await Bot.client.fetch_channel(channel_def[1])
        return channel
    else:
        Logger.log("Weird channel type", type=Logger.error)
        Logger.log(i, type=Logger.error)
    
    return None
    


def add_channel(id:int, channeltype: int, type: int, temp:bool=False) -> bool:
    # MAKE SURE WE DON'T EXCEED THE MAXIMUM AMOUNT OF CHANNELS
    # I DECIDED I WRITE IN ALL CAPS NOW.
    #THANK YOU FOR YOUR ATTENTION TO THIS MATTER
    if not len(channel_tree[type]["dm"] + channel_tree[type]["channel"]) < channel_tree[type]["max"] and not channel_tree[type]["max"] == -1:
        Logger.log(f"not exceeding max channels for type {channel_tree[type]["name"]}", type=Logger.warning)
        return False
    if id == -1: 
        Logger.log("Weird ID", type=Logger.error)
        return False # not successful
    if channeltype == TYPE_DM:
        channel_tree[type]["dm"].append(id)
    elif channeltype == TYPE_CHANNEL:
        channel_tree[type]["channel"].append(id)
    else:
        Logger.log("Weird channeltype", type=Logger.error)
        Logger.log(i, type=Logger.error)
        return False # not successful
    if not temp:
        Bot.Deweybase.write_data(statement=Bot.Deweybase.create_write_statement(table="channels",values=["id", "channeltype", "type"]),data=(id,channeltype,type))
    return True # success

def remove_channel(id:int, channeltype: int, type: int, temp:bool=False) -> bool:
    if id == -1: 
        Logger.log("Weird ID", type=Logger.error)
        return False # not successful
    if channeltype == TYPE_DM:
        while id in channel_tree[type]["dm"]:
            channel_tree[type]["dm"].remove(id)
    elif channeltype == TYPE_CHANNEL:
        while id in channel_tree[type]["channel"]:
            channel_tree[type]["channel"].remove(id)
    else:
        Logger.log("Weird channeltype", type=Logger.error)
        Logger.log(i, type=Logger.error)
        return False # not successful
    if not temp:
        Bot.Deweybase.write_data(statement=Bot.Deweybase.create_delete_statement(table="channels",where=["id", "channeltype", "type"]),data=(id,channeltype,type))
    return True # success

for i in channel_settings:
    add_channel(id=i[0],channeltype=i[1],type=i[2],temp=True)
    
Logger.log(channel_tree, type=Logger.verbose)
