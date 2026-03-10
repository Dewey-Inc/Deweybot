import discord
from discord.ext import commands, tasks
import Bot
import other.Permissions as Permissions


admin_group = discord.app_commands.Group(name="z-admin-other", description="g")



@admin_group.command(name="repeat", description="!-ADMIN ONLY-! repeat what said :thumbs_up:")
@discord.app_commands.allowed_installs(guilds=True, users=False)
async def adminrepeat(ctx : discord.Interaction, what_said: str, channel: discord.TextChannel | discord.Thread):
    if Permissions.is_override(ctx):
        await ctx.response.send_message(
            f"okay!", ephemeral=True
        )
        await channel.send(what_said)

if Bot.DeweyConfig["gacha-enabled"]:
    import gachalib
    if Bot.DeweyConfig["gacha-reminder-task"]:
        @admin_group.command(name="start-reminder-task", description="!-ADMIN ONLY-! restart reminder task")
        @discord.app_commands.allowed_installs(guilds=True, users=False)
        async def reminder_task(ctx : discord.Interaction):
            if Permissions.is_override(ctx):
                if not gachalib.reminder_task.is_running:
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
        async def check_reminder_task(ctx : discord.Interaction):
            if Permissions.is_override(ctx):
                await ctx.response.send_message(
                    gachalib.reminder_task.is_running, ephemeral=True
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

Bot.tree.add_command(admin_group)