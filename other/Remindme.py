import other.Logger as Logger
import Bot
import datetime
import discord
from discord.ext import tasks

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
        