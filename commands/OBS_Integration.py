from io import BytesIO

import discord
from discord.ext import commands
from discord.app_commands import AppCommandError
import Bot

import other.Permissions as Permissions

import subprocess, requests
import other.Logger as Logger

aa = None
running = False


class OBSCog(commands.cog.GroupCog, name="obs"):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        print("OBS Cog OBSing it")

            

    async def cog_app_command_error(self, interaction: discord.Interaction, error: AppCommandError) -> None:
        if isinstance(error, discord.app_commands.errors.CheckFailure):
            await interaction.response.send_message(content="Yo. You not part of the \"Gang\"")
        else:
            raise error


    
    @discord.app_commands.command(name="z-launch-server", description="cause uptown funk gonna give it to ya")
    @discord.app_commands.check(predicate=Permissions.admin_check)
    async def launch(self, ctx : discord.Interaction):
        global aa
        aa = subprocess.Popen([
            f"./server.py",
            "-H", Bot.DeweyConfig["obs-integration-host"],
            "-P", str(Bot.DeweyConfig["obs-integration-port"]),
            "-s", Bot.DeweyConfig["obs-integration-secret"]], cwd="./other/dewey_obs")
        Logger.log(" [OBS_Integration] launched Dewey OBS PID ", aa.pid, type=Logger.info)
        await ctx.response.send_message(f"i started it {aa.pid}")
        running = True


    @discord.app_commands.command(name="z-kill-server", description="cause uptown funk gonna give it to ya")
    @discord.app_commands.check(predicate=Permissions.admin_check)
    async def kill(self, ctx : discord.Interaction):
        if aa:
            aa.kill()
            running = False
            await ctx.response.send_message(content=f"i KILL ED it {aa.pid}")

    @discord.app_commands.command(name="z-send-image", description="cause uptown funk gonna give it to ya")
    @discord.app_commands.check(predicate=Permissions.admin_check)
    async def send(self, ctx : discord.Interaction, image : discord.Attachment):
        imaaage = BytesIO()
        await image.save(fp=imaaage)

        resp = requests.post(Bot.DeweyConfig["obs-integration-post-host"] + "/image",
                            headers={"Authorization": f"Bearer {Bot.DeweyConfig["obs-integration-secret"]}"},
                            files={"image": imaaage})
        if resp.status_code == 201:
            await ctx.response.send_message('Successfully sent image')
        elif resp.status_code == 401:
            await ctx.response.send_message('Error (incorrect secret)!!!!! ' + resp.content.decode())
        elif resp.status_code == 400:
            await ctx.response.send_message('Error (missing image)!!!!! ' + resp.content.decode())
        else:
            await ctx.response.send_message('Error (unknown)!!!!! ' + resp.content.decode())
            
        imaaage.close()



async def setup(bot:commands.Bot):
    print("Hi I am the obs integration extension")
    await bot.add_cog(OBSCog(bot=bot))

async def teardown(bot):
    print("Hi I am exiting the obs integration extension")