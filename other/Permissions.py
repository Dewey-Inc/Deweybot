from typing import Literal

import other.Logger as Logger
from discord.ext import commands
import discord
import Bot

TYPE_ROLE   = 1
TYPE_MEMBER = 2
PERMISSION_ADMIN           = 1
PERMISSION_GFAD_DISALLOWED = 2
PERMISSION_REPEAT          = 3
PERMISSION_GACHA_APPROVE   = 4

permission_literal = Literal["PERMISSION_ADMIN", "PERMISSION_GFAD_DISALLOWED", "PERMISSION_REPEAT", "PERMISSION_GACHA_APPROVE"]
type_literal       = Literal["TYPE_ROLE", "TYPE_MEMBER"]

permission_tree = {
    PERMISSION_ADMIN: {
        "name": "PERMISSION_ADMIN",
        "id": PERMISSION_ADMIN,
        "users": [],
        "roles": []
    },
    PERMISSION_GFAD_DISALLOWED: {
        "name": "PERMISSION_GFAD_DISALLOWED",
        "id": PERMISSION_GFAD_DISALLOWED,
        "users": [],
        "roles": []
    },
    PERMISSION_REPEAT: {
        "name": "PERMISSION_REPEAT",
        "id": PERMISSION_REPEAT,
        "users": [],
        "roles": []
    },
    PERMISSION_GACHA_APPROVE: {
        "name": "PERMISSION_GACHA_APPROVE",
        "id": PERMISSION_GACHA_APPROVE,
        "users": [],
        "roles": []
    }
}

permissions = Bot.Deweybase.read_data(statement=Bot.Deweybase.create_read_statement(table="permissions", values=["id","type","permission"]))


def admin_check(ctx:discord.Interaction) -> bool:                      return check_permission(ctx=ctx, permission=PERMISSION_ADMIN)
def gfad_disallowed_check(ctx:discord.Interaction) -> bool:            return check_permission(ctx=ctx, permission=PERMISSION_GFAD_DISALLOWED)
def repeat_check(ctx:discord.Interaction) -> bool:                     return check_permission(ctx=ctx, permission=PERMISSION_REPEAT)
def gacha_approve_check(ctx:discord.Interaction) -> bool:              return check_permission(ctx=ctx, permission=PERMISSION_GACHA_APPROVE)


#[y.id for y in ctx.user.roles]

def banned(ctx: discord.Interaction) -> bool:
    if ctx.guild_id == None:
        return False
    
    if isinstance(ctx.user, discord.User):
        return False

    user_roles = [y.id for y in ctx.user.roles]
    for i in user_roles:
        if i == Bot.DeweyConfig["banned-role"]:
            return True
    return False

def check_permission(ctx: discord.Interaction,permission:int) -> bool:
    if not permission == PERMISSION_ADMIN:
        if check_permission(ctx=ctx, permission=PERMISSION_ADMIN): return True
        
    if ctx.user.id in permission_tree[permission]["users"]:
        return True
    
    if type(ctx.user) == discord.Member:
        user_roles = [y.id for y in ctx.user.roles]
        for i in user_roles:
            if i in permission_tree[permission]["roles"]:
                return True
            
    return False

def add_permission(id:int, type: int, permission: int, temp:bool=False) -> bool:
    if type == TYPE_ROLE:
        permission_tree[permission]["roles"].append(id)
    elif type == TYPE_MEMBER:
        permission_tree[permission]["users"].append(id)
    else:
        Logger.log("Weird permission", type=Logger.error)
        Logger.log(i, type=Logger.error)
        return False # not successful
    if not temp:
        Bot.Deweybase.write_data(statement=Bot.Deweybase.create_write_statement(table="permissions",values=["id", "type", "permission"]),data=(id,type,permission))
    return True # success

def remove_permission(id:int, type: int, permission: int, temp:bool=False) -> bool:
    if type == TYPE_ROLE:
        while id in permission_tree[permission]["roles"]:
            permission_tree[permission]["roles"].remove(id)
    elif type == TYPE_MEMBER:
        while id in permission_tree[permission]["users"]:
            permission_tree[permission]["users"].remove(id)
    else:
        Logger.log("Weird permission", type=Logger.error)
        Logger.log(i, type=Logger.error)
        return False # not successful
    if not temp:
        Bot.Deweybase.write_data(statement=Bot.Deweybase.create_delete_statement(table="permissions",where=["id", "type", "permission"]),data=(id,type,permission))
    return True # success

for i in permissions:
    add_permission(id=i[0],type=i[1],permission=i[2],temp=True)
    
Logger.log(permission_tree, type=Logger.verbose)

def check_if_in_main_guid(ctx: discord.Interaction) -> bool:
    if Bot.client.main_guild is not None:
        return Bot.client.main_guild.get_member(ctx.user.id) is not None
    else:
        return False