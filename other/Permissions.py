from discord.ext import commands
import discord
import Bot

TYPE_ROLE   = 1
TYPE_MEMBER = 2
PERMISSION_ADMIN           = 1
PERMISSION_GFAD_DISALLOWED = 2
PERMISSION_REPEAT          = 3

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
    }
}

permissions = Bot.Deweybase.read_data(statement=Bot.Deweybase.create_read_statement(table="permissions", values=["id","type","permission"]))

for i in permissions:
    if i[1] == TYPE_ROLE:
        permission_tree[i[2]]["roles"].append(i[0])
    elif i[1] == TYPE_MEMBER:
        permission_tree[i[2]]["users"].append(i[0])
    else:
        print("Weird permission")
        print(i)

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
    if ctx.user.id in permission_tree[permission]["users"]:
        return True
    
    if type(ctx.user) == discord.Member:
        user_roles = [y.id for y in ctx.user.roles]
        for i in user_roles:
            if i in permission_tree[permission]["roles"]:
                return True
            
    return False

def check_if_in_main_guid(ctx: discord.Interaction) -> bool:
    if Bot.client.main_guild is not None:
        return Bot.client.main_guild.get_member(ctx.user.id) is not None
    else:
        return False