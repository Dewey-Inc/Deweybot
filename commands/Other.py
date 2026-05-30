
import typing

import Bot
import discord
from discord.app_commands import AppCommandError
from discord.ext import commands, tasks
import other.Permissions as Permissions
import other.Channels as Channels
import other.Logger as Logger

if Bot.DeweyConfig["gacha-enabled"]: # pylance doesn't like these and thinks they are possibly unbound
    import gachalib
if Bot.DeweyConfig["reminders-enabled"]:
    import other.Remindme as Remindme
if Bot.DeweyConfig["gif-enabled"]:
    import other.gif as gif

import random
import re

class OtherCog(Bot.DeweyCog, name="other"):
    def __init__(self, bot):
        self.bot = bot
        #self._last_member = None

    async def cog_load(self):
        Logger.log("Other Cog Dewin' it", type=Logger.info)

    @commands.Cog.listener()
    async def on_message(self, message):


        # Grog responses
        if Bot.DeweyConfig["grok-responses"]:
            if re.search(f"(@?grok|@?gork)", message.content.lower()):
                if random.random() < 0.02:
                    await message.reply("oh poor baby 🥺🥺 do you need the robot to make you pictures? 🥺🥺 yeah? 🥺🥺 do you need the bo-bot to write you essay too? yeah ??? you can't do it?? 🥺🥺 you're a moron??🥺🥺 do you need chat gpt to fuck your wife ?? 🥺🥺🥺")
                else:
                    await message.reply(random.choice([
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
                    ]))

            
        # Warf reactions
        if Bot.DeweyConfig["warf-reactions"]:
            if "warf" in message.content.lower():
                emoji = Bot.client.get_emoji(Bot.DeweyConfig["emoji-warf"])
                if not emoji:
                    raise ValueError("emoji-warf is not a valid emoji ID")
                else:
                    await message.add_reaction(emoji)

        # Suggestion reactions
        if Bot.DeweyConfig["suggestions-enabled"]:
            if message.channel.id == Channels.get_channels(channeltype=Channels.CHANNEL_SUGGESTIONS)[0][1] and not message.content.startswith("!"):
                await message.add_reaction("✅")
                await message.add_reaction("❌")
        return




    if Bot.DeweyConfig["gif-enabled"]:
        @discord.app_commands.command(name="house", description="house dr house md car accident funny gifs")
        @discord.app_commands.allowed_installs(guilds=True, users=True)
        async def house(self, ctx : discord.Interaction, text: str):
            if not Permissions.banned(ctx):
                await ctx.response.defer(thinking=True)
                
                image_file = discord.File(gif.gen(text),filename=f"{text.replace(" ", "_")[0:32]}.gif")
                await ctx.followup.send(file=image_file)
            else:
                await ctx.response.send_message(
                    f"You will be destroyed for your crimes.", ephemeral=True
                )


    if Bot.DeweyConfig["reminders-enabled"]:
        @discord.app_commands.command(name="remindme", description="Get a DM after X amount of time !")
        async def remindme(self, ctx : discord.Interaction, weeks:int=0, days:int=0, hours:int=0, minutes:int=0, note: str = ""):
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

    if Bot.DeweyConfig["nick-enabled"]:
        @discord.app_commands.command(name="nickname", description="Change someone's nickname")
        @discord.app_commands.allowed_installs(guilds=True, users=False)
        async def nickname(self, ctx : discord.Interaction, user: discord.Member | discord.User | None = None, nickname: str | None = None):
            try:
                if user == None:
                    user = ctx.user
                assert type(user) == discord.Member
                
                previous = user.nick
                await user.edit(nick=nickname)
                await ctx.response.send_message(
                    f"{Bot.DeweyConfig["emoji-dewey"]} Dewey blast! {Bot.DeweyConfig["emoji-dewey"]} (name changed `{previous}` -> `{nickname}`)", ephemeral=False
                )
            except Exception as e:
                if "403" in str(e):
                    await ctx.response.send_message(
                        "You cannot nick the server owner (403 error)", ephemeral=True
                    )
                elif "400" in str(e):
                    await ctx.response.send_message(
                        str(e), ephemeral=True
                    )
                else:
                    raise e


    @discord.app_commands.command(name="version", description="What version am I?")
    @discord.app_commands.allowed_installs(guilds=True, users=False)
    async def version(self, ctx):
        await ctx.response.send_message(
            f"Yo yo yo man, its the big dewbert!\n{Bot.version}", ephemeral=True
        )

    @discord.app_commands.command(name="sexer", description="Sexer")
    @discord.app_commands.allowed_installs(guilds=True, users=True)
    async def sexer(self, ctx):
        sexer = open("other/ytp_sexer.mp4", "rb")
        await ctx.response.send_message(file=discord.File(fp=sexer, filename="sexer.mp4"))
        sexer.close()

    #@discord.app_commands.command(name="Testcommand", description="echo test")
    #async def self(self, ctx : discord.Interaction, test_argument: str):
    #    await ctx.response.send_message(
    #        test_argument, ephemeral=True
    #    )



class AdminOtherCog(Bot.DeweyCog, name="z-admin-other"):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        Logger.log("Admin Other Cog Dewin' it", type=Logger.info)
    

    @discord.app_commands.command(name="repeat", description="!-ADMIN ONLY-! repeat what said :thumbs_up:")
    @discord.app_commands.allowed_installs(guilds=True, users=False)
    @discord.app_commands.check(predicate=Permissions.repeat_check)
    async def adminrepeat(self, ctx : discord.Interaction, what_said: str, channel: discord.TextChannel | discord.Thread | None = None, reply: str = "0"):
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

    # Won't work because of how the new system works with the tasks being defined inside the command files
    #if Bot.DeweyConfig["gacha-enabled"]:
    #    if Bot.DeweyConfig["gacha-reminder-task"]:
    #        @discord.app_commands.command(name="start-reminder-task", description="!-ADMIN ONLY-! restart reminder task")
    #        @discord.app_commands.allowed_installs(guilds=True, users=False)
    #        @discord.app_commands.check(predicate=Permissions.admin_check)
    #        async def reminder_task(self, ctx : discord.Interaction):
    #            if not Bot.botClient.get:
    #                gachalib.reminder_task.start()
    #                await ctx.response.send_message(
    #                    f"okay!", ephemeral=True
    #                )
    #            else:
    #                await ctx.response.send_message(
    #                    f"its running already", ephemeral=True
    #                )
    #        @discord.app_commands.command(name="check-reminder-task", description="!-ADMIN ONLY-! check if reminder task running")
    #        @discord.app_commands.allowed_installs(guilds=True, users=False)
    #        @discord.app_commands.check(predicate=Permissions.admin_check)
    #        async def check_reminder_task(self, ctx : discord.Interaction):
    #            await ctx.response.send_message(
    #                gachalib.reminder_task.is_running(), ephemeral=True
    #            )


    @discord.app_commands.command(name="assign_permission", description="!-ADMIN ONLY-! assign someone a permission")
    @discord.app_commands.allowed_installs(guilds=True, users=False)
    @discord.app_commands.check(predicate=Permissions.admin_check)
    async def assign_permission(self, ctx : discord.Interaction, permission:Permissions.permission_literal, what:Permissions.type_literal,object:discord.Role|discord.User):
        a = Permissions.add_permission(id=object.id,type=typing.get_args(Permissions.type_literal).index(what)+1,permission=typing.get_args(Permissions.permission_literal).index(permission)+1,temp=False)
        await ctx.response.send_message(content="Success" if a else "Malfunction")


    @discord.app_commands.command(name="remove_permission", description="!-ADMIN ONLY-! remove permission from someone")
    @discord.app_commands.allowed_installs(guilds=True, users=False)
    @discord.app_commands.check(predicate=Permissions.admin_check)
    async def remove_permission(self, ctx : discord.Interaction, permission:Permissions.permission_literal, what:Permissions.type_literal,object:discord.Role|discord.User):
        a = Permissions.remove_permission(id=object.id,type=typing.get_args(Permissions.type_literal).index(what)+1,permission=typing.get_args(Permissions.permission_literal).index(permission)+1,temp=False)
        await ctx.response.send_message(content="Success" if a else "Malfunction")


    @discord.app_commands.command(name="list_permission", description="!-ADMIN ONLY-! list everyone with a permission")
    @discord.app_commands.allowed_installs(guilds=True, users=False)
    @discord.app_commands.check(predicate=Permissions.admin_check)
    async def list_permission(self, ctx : discord.Interaction, permission:Permissions.permission_literal):
        permission_id = typing.get_args(Permissions.permission_literal).index(permission)+1
        users_embed = discord.Embed(title="Users", description="ok")
        roles_embed = discord.Embed(title="Roles", description="ok")

        for i in Permissions.permission_tree[permission_id]["users"]:
            users_embed.add_field(name=f"User", value=f"<@{i}>")
        for i in Permissions.permission_tree[permission_id]["roles"]:
            roles_embed.add_field(name=f"Role", value=f"<@&{i}>")

        await ctx.response.send_message(content=f"Permission for {permission}", embeds=[users_embed,roles_embed])


    @discord.app_commands.command(name="add_channel", description="!-ADMIN ONLY-! adds a channel to the channel lists")
    @discord.app_commands.allowed_installs(guilds=True, users=False)
    @discord.app_commands.check(predicate=Permissions.admin_check)
    async def add_channel(self, ctx : discord.Interaction, type: Channels.channel_literal, user: discord.User | None = None, channel:discord.TextChannel | None = None):
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


    @discord.app_commands.command(name="remove_channel", description="!-ADMIN ONLY-! removes a channel from the channel lists")
    @discord.app_commands.allowed_installs(guilds=True, users=False)
    @discord.app_commands.check(predicate=Permissions.admin_check)
    async def remove_channel(self, ctx : discord.Interaction, type: Channels.channel_literal, user: discord.User | None = None, channel:discord.TextChannel | None = None):
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


    @discord.app_commands.command(name="list_channel", description="!-ADMIN ONLY-! list channels with a type")
    @discord.app_commands.allowed_installs(guilds=True, users=False)
    @discord.app_commands.check(predicate=Permissions.admin_check)
    async def list_channel(self, ctx : discord.Interaction, type: Channels.channel_literal):
        channel_type_id = typing.get_args(Channels.channel_literal).index(type)+1
        dm_embed = discord.Embed(title="Dms", description="ok")
        channels_embed = discord.Embed(title="Channels", description="like actually whatever")

        for i in Channels.channel_tree[channel_type_id]["dm"]:
            dm_embed.add_field(name=f"Dms", value=f"<@{i}>")
        for i in Channels.channel_tree[channel_type_id]["channel"]:
            channels_embed.add_field(name=f"Role", value=f"<#{i}>")

        await ctx.response.send_message(content=f"Channels for {type}", embeds=[dm_embed,channels_embed])

    
    #@discord.app_commands.command(name="requires-staff", description="permission test")
    #async def self(self, ctx : discord.Interaction):
    #    has_perms = Permissions.has_permission(ctx=ctx,allowed=["staff"])
    #    Logger.log(has_perms, type=Logger.verbose)
    #    if has_perms:
    #        await ctx.response.send_message(
    #            f"ok", ephemeral=False
    #        )
    #    else:
    #        await ctx.response.send_message(
    #            f"not ok :(", ephemeral=False
    #        )
            

if Bot.DeweyConfig["reminders-enabled"]:
    @tasks.loop(name="remindme-task", minutes=1)
    async def remindme_task():
        Logger.log(" [EVIL REMINDER TASK] im runnninggg")
        reminders = Remindme.getReminders()
        reminder_qualifiers:list[Remindme.Reminder] = []

        timestamp = round(Remindme.datetime.datetime.now().timestamp())
        for user in reminders:
            if timestamp > user.when:
                reminder_qualifiers.append(user)

        
        for i in reminder_qualifiers:
            try:
                user = Bot.client.get_user(i.uid)
                if user == None: user = await Bot.client.fetch_user(i.uid)
                dm_channel = user.dm_channel
                if not dm_channel: dm_channel = await user.create_dm()
                
                await dm_channel.send(content=f"""Hello I'm here to remind you of a thing you left on <t:{i.made}> for <t:{i.when}>{f" (https://discord.com/channels/{i.guild}/{i.channel}/{i.message})" if i.guild and i.channel and i.message else ""}
{f"```{i.note}```" if i.note else ""}""")
            except discord.errors.Forbidden:
                pass

            #set the timeout to -2 so they don't qualify again (we don't dm them again)
            Remindme.removeReminder(uid=i.uid,when=i.when,made=i.made,messageid=i.message)



async def setup(bot:commands.Bot):
    Logger.log("Hi I am the other extension", type=Logger.info)

    if Bot.DeweyConfig["reminders-enabled"]:
        if not remindme_task.is_running():
            remindme_task.start()

    await bot.add_cog(OtherCog(bot=bot))
    await bot.add_cog(AdminOtherCog(bot=bot))

async def teardown(bot):
    Logger.log("Hi I am exiting the other extension", type=Logger.info)