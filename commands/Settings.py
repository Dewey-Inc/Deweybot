import Bot
import discord
from discord.app_commands import AppCommandError
from discord.ext import commands
import other.Permissions as Permissions
import other.Settings as Settings
import other.Logger as Logger


class SettingsCog(Bot.DeweyCog, name="obs"):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        Logger.log("Settings Cog Dewin' it", type=Logger.info)



    
    @discord.app_commands.command(name="z-debug-get", description="cause uptown funk gonna give it to ya")
    @discord.app_commands.check(predicate=Permissions.admin_check)
    async def get(self, ctx : discord.Interaction,name:str):
        a = Settings.Settings().get_setting(uid=ctx.user.id, name=name)
        await ctx.response.send_message(content=a, ephemeral=True)


    @discord.app_commands.command(name="z-debug-set", description="cause uptown funk gonna give it to ya")
    @discord.app_commands.check(predicate=Permissions.admin_check)
    async def set(self, ctx : discord.Interaction,name:str,value:bool):
        Settings.Settings().set_setting(uid=ctx.user.id, name=name, value=value)
        await ctx.response.send_message(content="ok", ephemeral=True)



async def setup(bot:commands.Bot):
    Logger.log("Hi I am the settings extension", type=Logger.info)
    await bot.add_cog(SettingsCog(bot=bot))

async def teardown(bot):
    Logger.log("Hi I am exiting the settings extension", type=Logger.info)