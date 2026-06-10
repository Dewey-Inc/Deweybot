import other.Logger as Logger
import Bot
import datetime
import discord
from discord.ext import tasks

class TimeSelectModal(discord.ui.Modal, title="When would you like to be reminded?"):
    m = discord.ui.TextInput(required=False, label="Minutes")
    h = discord.ui.TextInput(required=False, label="Hours")
    d = discord.ui.TextInput(required=False, label="Days")
    w = discord.ui.TextInput(required=False, label="Weeks")

    def __init__(self, reminder: Reminder) -> None:
        super().__init__()
        self.reminder = reminder

    async def on_submit(self, interaction: discord.Interaction):
        r = self.reminder
        now = datetime.datetime.today()
        m = int(self.m.value or 0)
        h = int(self.h.value or 0)
        d = int(self.d.value or 0)
        w = int(self.w.value or 0)
        delta = datetime.timedelta(minutes=m, hours=h, days=d, weeks=w)
        when = round((now+delta).timestamp())
        setReminder(r.uid, r.made, when, r.note, r.message, r.guild, r.channel)
        await interaction.response.send_message(
            content=f"You will be reminded again <t:{when}:R>"
        )

class RemindButton(discord.ui.Button):
    def __init__(self, reminder) -> None:
        self.reminder = reminder
        super().__init__(label="Remind me again later", style=discord.ButtonStyle.primary)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(TimeSelectModal(self.reminder))

class ReminderView(discord.ui.LayoutView):
    def __init__(self, reminder: Reminder) -> None:
        super().__init__(timeout=None)
        container = discord.ui.Container(
            discord.ui.TextDisplay("# Reminder"),
            discord.ui.TextDisplay(f"""Hello I'm here to remind you of a thing you left on <t:{reminder.made}>{f" (https://discord.com/channels/{reminder.guild}/{reminder.channel}/{reminder.message})"
                                   if reminder.guild and reminder.channel and reminder.message else ""} {f"```{reminder.note}```" if reminder.note else ""}"""),
            discord.ui.Separator(),
            discord.ui.ActionRow(RemindButton(reminder))
        )
        
        self.add_item(container)

if Bot.DeweyConfig["reminders-enabled"]:

    class Reminder:
        def __init__(self, uid:int, made:int, when:int, note:str, guild:int, channel:int, message:int):
            self.uid = uid
            self.made = made
            self.when = when
            self.note = note
            self.guild = guild
            self.channel = channel
            self.message = message


    def setReminder(uid: int, made: int, when: int, note: str, message: int|None,guild:int|None, channel:int|None) -> None:
        Bot.Deweybase.write_data(statement=Bot.Deweybase.create_write_statement(table="remindme",
        values=["uid","made","whenr","note","message","guild","channel"]), data=(uid,made,when,note,message,guild,channel))
        
    def removeReminder(uid:int,when:int,made:int,messageid:int|None) -> None:
        Bot.Deweybase.write_data(statement=Bot.Deweybase.create_delete_statement(table="remindme",
        where=["uid","whenr","made"] if not messageid else ["uid","whenr","made","message"]), data=(uid,when,made,)if not messageid else(uid,when,made,messageid,))
        
    def getReminders(whose: None | int = None) -> list[Reminder]:
        try:
            a = Bot.Deweybase.read_data(statement=Bot.Deweybase.create_read_statement(table="remindme",values=["uid","made","whenr","note","message","guild","channel"],
                                                                                      where=["uid"] if whose else []), parameters=(whose,) if whose else ())
            b = []

            for i in a:
                b.append(Reminder(uid=i[0],made=i[1],when=i[2],note=i[3],message=i[4],guild=i[5],channel=i[6]))

            return b
        except IndexError:
            return []
        
    @tasks.loop(name="remindme-task", minutes=1)
    async def remindme_task():
        Logger.log(" [EVIL REMINDER TASK] im runnninggg")
        reminders = getReminders()
        reminder_qualifiers:list[Reminder] = []

        timestamp = round(datetime.datetime.now().timestamp())
        for user in reminders:
            if timestamp > user.when:
                reminder_qualifiers.append(user)

        
        for i in reminder_qualifiers:
            try:
                user = Bot.client.get_user(i.uid)
                if user == None: user = await Bot.client.fetch_user(i.uid)
                dm_channel = user.dm_channel
                if not dm_channel: dm_channel = await user.create_dm()


                await dm_channel.send(view=ReminderView(i))
            except discord.errors.Forbidden:
                pass

            #set the timeout to -2 so they don't qualify again (we don't dm them again)
            removeReminder(uid=i.uid,when=i.when,made=i.made,messageid=i.message)
    
    Bot.client.on_ready_functions.append(remindme_task.start)