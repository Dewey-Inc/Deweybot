# we should maybe possibly refactor everything so we're not using 3 different names for it lol

import io
import discord
from discord.ext import commands, tasks
import Bot
import other.Permissions as Permissions
import other.Logger as Logger
import other.Channels as Channels
import datetime,random
import typing

info_msg = f"""In this server, a new mayor is randomly chosen every day. \
To qualify, you must have sent at least {Bot.DeweyConfig["kfad-must-have"]} messages in the last 2 weeks.

As mayor, you can:
* Post about whatver you feel like in your own channel (within rules)
* Change a letter in a channel's name
* Change a letter in Dewey's bio"""

gfad_group = discord.app_commands.Group(name="gfad", description="God for a day")

class GodView(discord.ui.LayoutView):
    def __init__(self, god:discord.Member|discord.User, end:datetime.datetime) -> None:
        super().__init__(timeout=None)
        container = discord.ui.Container(
            discord.ui.TextDisplay("# Mayor for the Day"),
            discord.ui.TextDisplay(f"{god.mention} is the Mayor for the Day (until <t:{round(end.timestamp())}:f>, "
                                   f"<t:{round(end.timestamp())}:R>! to have a chance to be Mayor make sure you're active in the server :)"),
            discord.ui.Separator(),
            InfoActionRow()
        )
        self.add_item(container)

class InfoActionRow(discord.ui.ActionRow):
    @discord.ui.button(label="More info", style=discord.ButtonStyle.secondary, row=0, custom_id="info")
    async def info_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await interaction.response.send_message(content=info_msg, ephemeral=True)

#    @discord.ui.button(label="Skip", style=discord.ButtonStyle.primary, row=0, custom_id="skip")
#    async def skip_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
#        await interaction.response.defer()
#        assert interaction.guild and type(interaction.user) == discord.Member, "skip ran outside guild"
#
#        if interaction.guild.get_role(Bot.DeweyConfig["kfad-role"]) in interaction.user.roles:
#            await roll_god(message_requirement=Bot.DeweyConfig["kfad-must-have"], days=14, exclude_prev_gods=True)
#            await interaction.delete_original_response()
#        else:
#            await interaction.followup.send(content="Only the current mayor can do this!", ephemeral=True)

    @discord.ui.button(label="Opt out", style=discord.ButtonStyle.danger, row=0, custom_id="opt-out")
    async def optout_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        Permissions.add_permission(id=interaction.user.id, type=2, permission=typing.get_args(Permissions.permission_literal).index("PERMISSION_GFAD_DISALLOWED")+1)
        await interaction.response.send_message(content="You will no longer be able to recieve this role!", ephemeral=True)


async def roll_god(message_requirement, days, exclude_prev_gods):
    godchannel = await Channels.get_channel(channel_def=Channels.get_channels(channeltype=Channels.CHANNEL_GOD_CHANNEL,filtertype=Channels.TYPE_CHANNEL)[0])
    assert isinstance(godchannel,(discord.TextChannel,discord.Thread)), "god channel assertion"
    
    range_now = datetime.datetime.today()
    range_start = range_now - datetime.timedelta(days=days)
    range_end = range_now

    assert Bot.client.main_guild, "Bot.client.main_guild assertion"
    qualifiers, _ = await get_qualifiers(message_requirement=message_requirement, range_start=range_start, range_end=range_end,guild=Bot.client.main_guild,getmembers=True, exclude_prev_gods=exclude_prev_gods)
    
    if len(qualifiers) == 0:
        await godchannel.send(content=f"(There aren't enough people who qualify)", silent=True)
        return
    
    pick = random.choice(qualifiers)
    role = Bot.client.main_guild.get_role(Bot.DeweyConfig["kfad-role"])
    assert role, "could not find role"

    for i in role.members:
        await i.remove_roles(role, reason="god for a day roll")
    
    if type(pick) == discord.Member:
        await pick.add_roles(role,reason="god got a day!!!!")

    view = GodView(pick, range_now+datetime.timedelta(days=1))
    await godchannel.send(view=GodView(pick, range_now+datetime.timedelta(days=1)))


async def get_qualifiers(message_requirement:int, range_start:datetime.datetime, range_end:datetime.datetime,
                         guild:discord.Guild,getmembers:bool,exclude_prev_gods:bool=True) -> tuple[list[discord.Member | discord.User], dict[str,int]]:
    unique_authors: dict[str, int] = {}
    not_allowed: list[int] = []
    qualifiers: list[discord.Member | discord.User] = []

    gfad_channels_with_type = Channels.get_channels(channeltype=Channels.CHANNEL_GFAD_SEARCH,filtertype=Channels.TYPE_CHANNEL)
    gfad_channels = []
    for i in gfad_channels_with_type:
        gfad_channels.append(i[1])
    godchannel = await Channels.get_channel(channel_def=Channels.get_channels(channeltype=Channels.CHANNEL_GOD_CHANNEL,filtertype=Channels.TYPE_CHANNEL)[0])

    if exclude_prev_gods:
        assert isinstance(godchannel,(discord.TextChannel,discord.Thread)), "god channel assertion"
        assert godchannel
        async for message in godchannel.history(limit=None, before=range_end, after=range_start):
            if not message.author.id in not_allowed:
                not_allowed.append(message.author.id)

    for i in gfad_channels:
        cool_channel = Bot.client.get_channel(i)
        if cool_channel == None: cool_channel = await Bot.client.fetch_channel(i)

        assert not isinstance(cool_channel,(discord.ForumChannel,discord.CategoryChannel,discord.abc.PrivateChannel)), f"channel assertion '{i}' did not yeild usable channel"
        async for message in cool_channel.history(limit=None, before=range_end, after=range_start):
            #just get unique users first
            if not message.author.id in not_allowed:
                if message.author.bot: not_allowed.append(message.author.id)
                else: 
                    if type(message.author) == discord.Member:
                        if Permissions.check_permission(ctx=message.author, permission=Permissions.PERMISSION_GFAD_DISALLOWED):
                            not_allowed.append(message.author.id)

                        if not message.author.id in not_allowed:
                            if str(message.author.id) in unique_authors:
                                unique_authors[str(message.author.id)] += 1
                            else:
                                unique_authors[str(message.author.id)] = 1
                    else:
                        not_allowed.append(message.author.id)

    if getmembers:
        for uid,messagecount in unique_authors.items():
            if messagecount >= message_requirement:
                user = guild.get_member(int(uid))
                if user == None: user = await guild.fetch_member(int(uid))

                qualifiers.append(user)

    return (qualifiers, unique_authors)

@gfad_group.command(name="help", description="What is a 'god' and why for a day?")
async def gfad_help(ctx : discord.Interaction):
    await ctx.response.send_message(content="Test!", ephemeral=True)


@gfad_group.command(name="z-transfer", description="! ADMIN ONLY ! mod transfer god")
@discord.app_commands.check(predicate=Permissions.admin_check)
async def gfad_transfer(ctx : discord.Interaction, pick : discord.Member):
    await ctx.response.defer(ephemeral=False,thinking=True)

    if not ctx.guild:
        await ctx.followup.send("you must run this in the main server")
        return

    role = ctx.guild.get_role(Bot.DeweyConfig["kfad-role"])
    assert role, "could not find role"
    for i in role.members:
        await i.remove_roles(role, reason="god for a day roll")
        
    if type(pick) == discord.Member:
        await pick.add_roles(role,reason="god got a day!!!!")

    await ctx.followup.send("successfully transfer")


@gfad_group.command(name="z-roll", description="! ADMIN ONLY ! Roll GOD 🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲🎲")
@discord.app_commands.check(predicate=Permissions.admin_check)
async def gfad_roll(ctx : discord.Interaction, message_requirement:int = -1, days:int = 14, exclude_previous_gods:bool=True):
    if message_requirement == -1: message_requirement = Bot.DeweyConfig["kfad-must-have"]
    await ctx.response.defer()

    await roll_god(days=days, exclude_prev_gods=exclude_previous_gods, message_requirement=message_requirement)
    await ctx.delete_original_response()

@gfad_group.command(name="z-get-qualifiers", description="! ADMIN ONLY ! Get people who qualify")
@discord.app_commands.check(predicate=Permissions.admin_check)
async def gfad_get_qualifiers(ctx : discord.Interaction, message_requirement:int = -1, exclude_prev_gods:bool=True, days:int = 7):
    if message_requirement == -1: message_requirement = Bot.DeweyConfig["kfad-must-have"]
    range_now = datetime.datetime.today()
    range_start = range_now - datetime.timedelta(days=days)
    range_end = range_now
        
    await ctx.response.defer(ephemeral=False, thinking=True)

    assert ctx.guild, "ctx.guild assertion"
    _,qualifiers = await get_qualifiers(message_requirement=message_requirement, range_start=range_start, range_end=range_end,guild=ctx.guild,getmembers=False,exclude_prev_gods=exclude_prev_gods)
    qualifier_count = {}

    if len(qualifiers) == 0:
        await ctx.followup.send(content=f"(Nobody qualifies)", ephemeral=False)
        return
        
    for uid,messagecount in qualifiers.items():
        if messagecount >= message_requirement:
            qualifier_count[str(uid)] = messagecount

    string = ""
    for uid,count in qualifier_count.items():
        loser = ctx.guild.get_member(uid)
        if loser == None: loser = await ctx.guild.fetch_member(uid)

        string += loser.name + ": " + str(count) + "\n"
        
    buffer = io.BytesIO()
    buffer.write(string.encode())
    buffer.seek(0)
    await ctx.followup.send(content=f"Qualifiers <t:{round(range_start.timestamp())}>-<t:{round(range_end.timestamp())}>",file=discord.File(fp=buffer,filename="abc.txt"))

if Bot.DeweyConfig["kfad-auto"]:
    run = datetime.time(hour=15, minute=00, second=00, tzinfo=datetime.timezone(datetime.timedelta(hours=-4),"EDT"))

    @tasks.loop(name="remindme-task", time=run)
    async def kfad_task():
        Logger.log(" [king for a day] im runnninggg", type=Logger.info)
        
        godchannel = await Channels.get_channel(channel_def=Channels.get_channels(channeltype=Channels.CHANNEL_GOD_CHANNEL,filtertype=Channels.TYPE_CHANNEL)[0])
        assert isinstance(godchannel,(discord.TextChannel,discord.Thread)), "god channel assertion"

        await godchannel.send("Hello! I'm *Dewey*, the one in the electoral college or something. I'm gonna roll a dice!")
        await roll_god(message_requirement=Bot.DeweyConfig["kfad-must-have"], days=14, exclude_prev_gods=True)
    
    Bot.client.on_ready_functions.append(kfad_task.start)

Bot.tree.add_command(gfad_group)