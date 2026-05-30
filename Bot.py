import other.Logger as Logger

if __name__ == "__main__":
    Logger.log("Don't run Bot.py please, run StartBot.py", type=Logger.fatal)
    exit()

import io
from types import CoroutineType, FunctionType, MethodType
import discord
from discord.ext import tasks, commands
from discord.abc import PrivateChannel
from yaml import load,Loader
import traceback
from inspect import iscoroutinefunction
from subprocess import check_output, CalledProcessError

with open("dewey.yaml", "r") as f:
    DeweyConfig = load(stream=f, Loader=Loader)


try:
    version = check_output(["git", "branch", "--show-current"]).strip() + b"-" + check_output(["git", "rev-parse", "--short", "HEAD"]).strip()
    version = version.decode()
except CalledProcessError:
    version = "unknown"

intents = discord.Intents.all()


import db_lib
Deweybase = db_lib.setup_db(name="dewey")

import other.Permissions as Permissions
import other.Channels as Channels
import other.Settings as Settings

class botClient(discord.Client):
    def __init__(self):
        super().__init__(intents = discord.Intents.all())
        self.main_guild: discord.Guild | None
        self.synced = False
        self.already_ran_once = False
        self.on_ready_functions: list[MethodType | FunctionType] = []
        self.on_message_functions: list[CoroutineType | FunctionType] = []

    async def on_ready(self):
        if not self.already_ran_once:
            for i in self.on_ready_functions:
                if isinstance(i, (MethodType, FunctionType)):
                    Logger.log(f" [on_ready] running on_ready_function of {i.__name__}", type=Logger.info)
                    if iscoroutinefunction(i):
                        await i.__call__()
                    else:
                        i.__call__()

        self.main_guild = self.get_guild(DeweyConfig["main-guild"])

        await self.wait_until_ready()
        if not self.synced:
            await tree.sync()
            self.synced = True
           
        await self.change_presence(activity=discord.Activity(name=f"Dewin' it ({version})", type=3))


        Logger.log(f" [on_ready] Dewey'd as {self.user}", type=Logger.info)
        self.already_ran_once = True


    async def on_message(self, message: discord.Message):
        for i in self.on_message_functions:
            if iscoroutinefunction(i):
                await i.__call__(message)


    async def on_raw_reaction_add(self, reactionpayload: discord.RawReactionActionEvent):
        # remove conflicting vote reactions
        if reactionpayload.channel_id == Channels.get_channels(channeltype=Channels.CHANNEL_SUGGESTIONS)[0][1] and DeweyConfig["suggestions-enabled"]:
            if not reactionpayload.emoji.name in ["✅","❌"]: return
            assert self.user, "user is none"
            if reactionpayload.user_id == self.user.id: return
            
            reaction_channel = await client.fetch_channel(reactionpayload.channel_id)
            assert not isinstance(reaction_channel,(discord.ForumChannel,discord.CategoryChannel,PrivateChannel)), "reaction_channel assertion"
            message = await reaction_channel.fetch_message(reactionpayload.message_id)

            for i in message.reactions:
                reactors = [discord.Object(id=user.id) async for user in i.users()]
                snowflake = discord.Object(id=reactionpayload.user_id)
                
                if i.emoji == "✅" and reactionpayload.emoji.name == "❌":
                    if snowflake in reactors:
                        await message.remove_reaction(i.emoji, snowflake)
                elif i.emoji == "❌" and reactionpayload.emoji.name == "✅":
                    if snowflake in reactors:
                        await message.remove_reaction(i.emoji, snowflake)
        
        return
    
    async def on_error(self, event, error = None):
        a = traceback.format_exc()
        Logger.log(a, type=Logger.error)
        channel = await Channels.get_channel(channel_def=Channels.get_channels(channeltype=Channels.CHANNEL_ERRORS)[0])
        buffer = io.BytesIO()
        buffer.write(a.encode())
        buffer.seek(0)
        assert isinstance(channel,(discord.TextChannel, discord.Thread, discord.DMChannel)), "error channel assertion"
        await channel.send(f"<@322495136108118016> got an report for you boss (event {event})\n",file=discord.File(fp=buffer,filename="error.txt"))
        buffer.close()


client = botClient()
tree = discord.app_commands.CommandTree(client, allowed_contexts=discord.app_commands.AppCommandContext(guild=True,dm_channel=True,private_channel=True),
                                        allowed_installs=discord.app_commands.AppInstallationType(guild=True,user=True))

@tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    async def inform(ctx:discord.Interaction,message:str,ephemeral:bool=True):
        if ctx.response.is_done():
            await ctx.followup.send(content=message)
        else:
            await ctx.response.send_message(content=message)
        
    if isinstance(error, discord.app_commands.errors.CheckFailure):
        await inform(ctx=interaction, message="Yo. You not part of the \"Gang\"",ephemeral=True)
    else:
        a = traceback.format_exc()
        Logger.log(a, type=Logger.error)
        channel = await Channels.get_channel(channel_def=Channels.get_channels(channeltype=Channels.CHANNEL_ERRORS)[0])
        buffer = io.BytesIO()
        buffer.write(a.encode())
        buffer.seek(0)
        assert isinstance(channel,(discord.TextChannel, discord.Thread, discord.DMChannel)), "error channel assertion"
        await channel.send(f"<@322495136108118016> got an report for you boss (FROM ON_APP_COMMAND_ERROR)\n",file=discord.File(fp=buffer,filename="error.txt"))
        buffer.close()
        
        await interaction.followup.send(content="Ay! I gotted an error! Please ping the owners of me!")

if DeweyConfig["nick-enabled"]: import commands.Nick
if DeweyConfig["gacha-enabled"]: import commands.Gacha
if DeweyConfig["gif-enabled"]: import commands.Gif
if DeweyConfig["kfad-enabled"]: import commands.KFAD
if DeweyConfig["deweycoins-enabled"]: import commands.Bank
if DeweyConfig["obs-integration-enabled"]: import commands.OBS_Integration
import commands.Settings
import commands.Other

# RUN

client.run(token=DeweyConfig["token"])


