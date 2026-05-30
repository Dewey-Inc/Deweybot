import Bot
import discord
from discord.app_commands import AppCommandError
from discord.ext import commands
import other.Permissions as Permissions
import other.Settings as Settings


class SettingsCog(commands.cog.GroupCog, name="obs"):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        print("Settings Cog Dewin' it")

            

    async def cog_app_command_error(self, interaction: discord.Interaction, error: AppCommandError) -> None:
        if isinstance(error, discord.app_commands.errors.CheckFailure):
            await interaction.response.send_message(content="Yo. You not part of the \"Gang\"")
        else:
            raise error


    
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
    print("Hi I am the settings extension")
    await bot.add_cog(SettingsCog(bot=bot))

async def teardown(bot):
    print("Hi I am exiting the settings extension")
    await bot.remove_cog(SettingsCog.__name__)