
import typing

import discord
from discord.ext import commands, tasks
import Bot
import other.Permissions as Permissions
import other.Channels as Channels
import random
import re


admin_group = discord.app_commands.Group(name="z-admin-other", description="g")

if Bot.DeweyConfig["reminders-enabled"]:
    import other.Remindme as Remindme

    
    @Bot.tree.command(name="remindme", description="Get a DM after X amount of time !")
    async def remindme(ctx : discord.Interaction, weeks:int=0, days:int=0, hours:int=0, minutes:int=0, note: str = ""):
        if weeks == 0 and days == 0 and hours == 0 and minutes == 0:
            await ctx.response.send_message("you have to select a time", ephemeral=True)
            return
        if len(note) > 256:
            await ctx.response.send_message("you should shorten your note")
            return

        now = Remindme.datetime.datetime.today()
        delta = Remindme.datetime.timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes)
        when = round((now+delta).timestamp())

        message = await ctx.response.send_message("I'll dm you on " + str(now+delta) + f" (<t:{when}>) ")
        
        Remindme.setReminder(uid=ctx.user.id,made=round(now.timestamp()),when=when,note=note,message=message.message_id,guild=ctx.guild_id,channel=ctx.channel_id)
        Remindme.getReminders()

responses = [
    "It is certain", "Reply hazy, try again", "Don't count on it",
    "It is decidedly so", "Ask again later", "My reply is no",
    "Without a doubt", "Better not tell you now", "My sources say no",
    "Yes definitely", "Cannot predict now", "Outlook not so good",
    "You may rely on it", "Concentrate and ask again", "Very doubtful",
    "As I see it, yes",
    "Most likely",
    "Outlook good",
    "Yes",
    "Signs point to yes"
]


if Bot.DeweyConfig["warf-reactions"]:
    async def warf_react(message: discord.Message):
        assert Bot.client.user
        if "warf" in message.content.lower():
            emoji = Bot.client.get_emoji(Bot.DeweyConfig["emoji-warf"])
            if not emoji:
                raise ValueError("emoji-warf is not a valid emoji ID")
            else:
                await message.add_reaction(emoji)
    Bot.client.on_message_functions.append(warf_react)

if Bot.DeweyConfig["grok-responses"]:
    async def grok_response_message(message: discord.Message):
        assert Bot.client.user
        if re.search(f"(@?grok|@?gork)", message.content.lower()):
            if random.random() < 0.02:
                await message.reply("oh poor baby 🥺🥺 do you need the robot to make you pictures? 🥺🥺 yeah? 🥺🥺 do you need the bo-bot to write you essay too? yeah ??? you can't do it?? 🥺🥺 you're a moron??🥺🥺 do you need chat gpt to fuck your wife ?? 🥺🥺🥺")
            else:
                await message.reply(random.choice(responses))
            return
    Bot.client.on_message_functions.append(grok_response_message)

if Bot.DeweyConfig["suggestions-enabled"]:
    async def suggestions_reaction_message(message: discord.Message):
        if message.author == Bot.client.user:
            pass
        if message.channel.id == Channels.get_channels(channeltype=Channels.CHANNEL_SUGGESTIONS)[0][1] and not message.content.startswith("!"):
            await message.add_reaction("✅")
            await message.add_reaction("❌")
        return
    Bot.client.on_message_functions.append(suggestions_reaction_message)

if Bot.DeweyConfig["honeypot"]:
    async def honeypot_handler(message: discord.Message):
        channels = Channels.get_channels(channeltype=Channels.CHANNEL_HONEYPOT)
        channels_actual = []
        for i in channels:
            if i[0] == 2:
                channels_actual.append(await Channels.get_channel(channel_def=i))

        if message.channel in channels_actual: #OOPS SOMEONE SENT SOMETHING IN THE HONEYPOT
            if not Permissions.check_permission(ctx=message.author, permission=Permissions.PERMISSION_HONEYPOT_EXEMPT): # OOPS THEY ARENT EXEMPT
                assert isinstance(message.author, discord.Member), "the honeypot channel had a message with a user instead of a member"
                assert Bot.client.main_guild, "no main guild"
                role = Bot.client.main_guild.get_role(Bot.DeweyConfig["honeypot-ban-role"]) 
                assert role, "could not find role" # my beautiful tri-assertion beam
                await message.author.add_roles(role, reason="honeypot activation")

                channeldef = Channels.get_channels(channeltype=Channels.CHANNEL_ERRORS)
                print(channeldef)
                if not len(channeldef) == 0:
                    channel = await Channels.get_channel(channel_def=channeldef[0])

                    assert isinstance(channel,(discord.TextChannel, discord.Thread, discord.DMChannel)), "error channel assertion"
                    await channel.send(f"UID {message.author.id} \"{message.author.display_name}\" just activated my sweet... delicious... honey...")

    Bot.client.on_message_functions.append(honeypot_handler)


@admin_group.command(name="repeat", description="!-ADMIN ONLY-! repeat what said :thumbs_up:")
@discord.app_commands.allowed_installs(guilds=True, users=False)
@discord.app_commands.check(predicate=Permissions.repeat_check)
async def adminrepeat(ctx : discord.Interaction, what_said: str, channel: discord.TextChannel | discord.Thread | None = None, reply: str = "0"):
    log_channel = await Channels.get_channel(channel_def=Channels.get_channels(channeltype=Channels.CHANNEL_REPEAT_LOG)[0])

    assert isinstance(log_channel,(discord.TextChannel,discord.Thread,discord.DMChannel)), "log channel assertion"

    _channel = channel

    if _channel == None:
        _channel = ctx.channel

    assert _channel, "channel assertion"
    assert not isinstance(_channel, (discord.CategoryChannel,discord.ForumChannel)), "channel is category or forum assertion"

    if reply == "0":
        await _channel.send(content=what_said)
    else:
        reply_int = int(reply)
        reply_message = await _channel.fetch_message(reply_int)
        await reply_message.reply(content=what_said)

    await ctx.response.send_message(
        f"okay!", ephemeral=True
    )
    await log_channel.send(f"{ctx.user.name} said `{what_said}`")

if Bot.DeweyConfig["gacha-enabled"]:
    import gachalib
    if Bot.DeweyConfig["gacha-reminder-task"]:
        @admin_group.command(name="start-reminder-task", description="!-ADMIN ONLY-! restart reminder task")
        @discord.app_commands.allowed_installs(guilds=True, users=False)
        @discord.app_commands.check(predicate=Permissions.admin_check)
        async def reminder_task(ctx : discord.Interaction):
            if not gachalib.reminder_task.is_running():
                gachalib.reminder_task.start()
                await ctx.response.send_message(
                    f"okay!", ephemeral=True
                )
            else:
                await ctx.response.send_message(
                    f"its running already", ephemeral=True
                )
        @admin_group.command(name="check-reminder-task", description="!-ADMIN ONLY-! check if reminder task running")
        @discord.app_commands.allowed_installs(guilds=True, users=False)
        @discord.app_commands.check(predicate=Permissions.admin_check)
        async def check_reminder_task(ctx : discord.Interaction):
            await ctx.response.send_message(
                gachalib.reminder_task.is_running(), ephemeral=True
            )


@Bot.tree.command(name="version", description="What version am I?")
@discord.app_commands.allowed_installs(guilds=True, users=False)
async def version(ctx : discord.Interaction):
    await ctx.response.send_message(
        f"Yo yo yo man, its the big dewbert!\n{Bot.version}", ephemeral=True
    )

@Bot.tree.command(name="sexer", description="Sexer")
@discord.app_commands.allowed_installs(guilds=True, users=True)
async def sexer(ctx : discord.Interaction):
    sexer = open("other/ytp_sexer.mp4", "rb")
    await ctx.response.send_message(file=discord.File(fp=sexer, filename="sexer.mp4"))
    sexer.close()



@admin_group.command(name="assign_permission", description="!-ADMIN ONLY-! assign someone a permission")
@discord.app_commands.allowed_installs(guilds=True, users=False)
@discord.app_commands.check(predicate=Permissions.admin_check)
async def assign_permission(ctx : discord.Interaction, permission:Permissions.permission_literal, what:Permissions.type_literal,object:discord.Role|discord.User):
    a = Permissions.add_permission(id=object.id,type=typing.get_args(Permissions.type_literal).index(what)+1,permission=typing.get_args(Permissions.permission_literal).index(permission)+1,temp=False)
    await ctx.response.send_message(content="Success" if a else "Malfunction")

@admin_group.command(name="remove_permission", description="!-ADMIN ONLY-! remove permission from someone")
@discord.app_commands.allowed_installs(guilds=True, users=False)
@discord.app_commands.check(predicate=Permissions.admin_check)
async def remove_permission(ctx : discord.Interaction, permission:Permissions.permission_literal, what:Permissions.type_literal,object:discord.Role|discord.User):
    a = Permissions.remove_permission(id=object.id,type=typing.get_args(Permissions.type_literal).index(what)+1,permission=typing.get_args(Permissions.permission_literal).index(permission)+1,temp=False)
    await ctx.response.send_message(content="Success" if a else "Malfunction")

@admin_group.command(name="list_permission", description="!-ADMIN ONLY-! list everyone with a permission")
@discord.app_commands.allowed_installs(guilds=True, users=False)
@discord.app_commands.check(predicate=Permissions.admin_check)
async def list_permission(ctx : discord.Interaction, permission:Permissions.permission_literal):
    permission_id = typing.get_args(Permissions.permission_literal).index(permission)+1
    list_embed = discord.Embed(title="Permissions", description="ok")

    user = "<@" + ">\n<@".join(str(Channels.channel_tree[permission_id]["dm"])) +">"
    role = "<@&" + ">\n<#".join(str(Channels.channel_tree[permission_id]["channel"])) + ">"

    list_embed.add_field(name=f"Users", value=f"{user}")
    list_embed.add_field(name=f"Roles", value=f"{role}")

    await ctx.response.send_message(content=f"Permission for {permission} ({"inherits admin" if Permissions.permission_tree[permission_id]["inherit_admin"] else "does not inherit from admin"})",
                                    embeds=[list_embed])



@admin_group.command(name="add_channel", description="!-ADMIN ONLY-! adds a channel to the channel lists")
@discord.app_commands.allowed_installs(guilds=True, users=False)
@discord.app_commands.check(predicate=Permissions.admin_check)
async def add_channel(ctx : discord.Interaction, type: Channels.channel_literal, user: discord.User | None = None, channel:discord.TextChannel | None = None):
    if channel and user: 
        await ctx.response.send_message(content="Don't do them both. Bad things will happen. To you. And only you.")
        return 
    if not channel and not user: 
        await ctx.response.send_message(content="I'm going to kill you.") # Jokes
        return 

    a = Channels.add_channel(
        id=channel.id if channel else user.id if user else -1,
        channeltype=Channels.TYPE_DM if user else Channels.TYPE_CHANNEL if channel else -1,
        type=typing.get_args(Channels.channel_literal).index(type)+1,
        temp=False
    )

    await ctx.response.send_message(content="Success" if a else "Malfunction")

@admin_group.command(name="remove_channel", description="!-ADMIN ONLY-! removes a channel from the channel lists")
@discord.app_commands.allowed_installs(guilds=True, users=False)
@discord.app_commands.check(predicate=Permissions.admin_check)
async def remove_channel(ctx : discord.Interaction, type: Channels.channel_literal, user: discord.User | None = None, channel:discord.TextChannel | None = None):
    if channel and user: 
        await ctx.response.send_message(content="Don't do them both. Bad things will happen. To you. And only you.")
        return 
    if not channel and not user: 
        await ctx.response.send_message(content="I'm going to kill you.") # Jokes
        return 

    a = Channels.remove_channel(
        id=channel.id if channel else user.id if user else -1,
        channeltype=Channels.TYPE_DM if user else Channels.TYPE_CHANNEL if channel else -1,
        type=typing.get_args(Channels.channel_literal).index(type)+1,
        temp=False
    )

    await ctx.response.send_message(content="Success" if a else "Malfunction")

@admin_group.command(name="list_channel", description="!-ADMIN ONLY-! list channels with a type")
@discord.app_commands.allowed_installs(guilds=True, users=False)
@discord.app_commands.check(predicate=Permissions.admin_check)
async def list_channel(ctx : discord.Interaction, type: Channels.channel_literal):
    channel_type_id = typing.get_args(Channels.channel_literal).index(type)+1
    list_embed = discord.Embed(title="Channels", description="ok")

    dm = "<@" + ">\n<@".join(str(Channels.channel_tree[channel_type_id]["dm"])) + ">"
    channel = "<#" + ">\n<#".join(str(Channels.channel_tree[channel_type_id]["channel"])) + ">"

    list_embed.add_field(name=f"DMs", value=f"{dm}")
    list_embed.add_field(name=f"Channels", value=f"{channel}")

    await ctx.response.send_message(content=f"Channels for {type}" + 
                                    f"(count {Channels.channel_tree[channel_type_id]["dm"] + Channels.channel_tree[channel_type_id]["channel"]}/{Channels.channel_tree[channel_type_id]["max"]})" 
                                    if not Channels.channel_tree[channel_type_id]["max"] == -1 else "", embeds=[list_embed])


Bot.tree.add_command(admin_group)
