#! /usr/bin/env python3

from yaml import load,Loader
import sqlite3, pymysql

with open("dewey.yaml", "r") as f:
    DeweyConfig = load(stream=f, Loader=Loader)

tabletype = tuple[str, list[tuple[str, str]]]
tablestype = list[tabletype]

GachaTables: tablestype = [
    ("gacha", [
        ("maker_id",           "INTEGER"),
        ("request_message_id", "INTEGER"),
        ("id",                 "INTEGER"),
        ("accepted",           "BOOL"),
        ("name",               "varchar(256)"),
        ("description",        "varchar(256)"),
        ("rarity",             "varchar(256)"),
        ("filename",           "varchar(256)"),
    ]),
    ("gacha_user", [
        ("user_id",  "INTEGER"),
        ("last_use", "INTEGER"),
    ]),
    ("gacha_cards", [
        ("id",      "INTEGER"),
        ("card_id", "INTEGER"),
        ("user_id", "INTEGER"),
    ]),
]

CoinsTables: tablestype = [
    ("deweycoins", [
        ("uid",	            "INTEGER"),
        ("balance",	        "INTEGER"),
        ("highestbalance",	"INTEGER"),
        ("transactions",	"INTEGER"),
        ("spent",	        "INTEGER"),
        ("totalearned", 	"INTEGER"),
        ("lostgambling",    "INTEGER"),
        ("gainedgambling",  "INTEGER"),
        ("heads",           "INTEGER"),
        ("tails",           "INTEGER")
    ]),
]

ReminderTables: tablestype = [
    ("remindme", [
        ("uid",	    "INTEGER"),
        ("made",	"INTEGER"),
        ("whenr",	"INTEGER"),
        ("note",	"varchar(256)"),
        ("guild",   "INTEGER"),
        ("channel", "INTEGER"),
        ("message", "INTEGER"),
    ]),
]

SettingsTables: tablestype = [
    ("settings", [
        ("uid",              "INTEGER"),
        ("roll_reminder_dm", "bool"),
        ("roll_auto_sell",   "bool"),
    ]),
]

def makeCreateStatement(table:tabletype) -> str:
    fields = ""

    for i in range(len(table[1])):
        # create '"name" TYPE,'
        fields += f" {table[1][i][0]} {table[1][i][1]}{',' if not i+1==len(table[1]) else ''}\n"

    definition = f"CREATE TABLE {table[0]} (\n{fields});"

    return definition

if __name__ == "__main__":
    print("Yo yo yo! Welcome to the Dewey Database maker")

    #gacha_database = db_lib.setup_db(name="gacha", file=Bot.DeweyConfig["gacha-sqlite-path"])
    definitions = []

    for i in GachaTables:
        definitions.append(makeCreateStatement(table=i))
    for i in CoinsTables:
        definitions.append(makeCreateStatement(table=i))
    for i in ReminderTables:
        definitions.append(makeCreateStatement(table=i))
    for i in SettingsTables:
        definitions.append(makeCreateStatement(table=i))

    #print(definitions)

    if DeweyConfig["database-type"] == "SQLite3":
        print("creating SQLite3")
        print(f"creating new db @{DeweyConfig["dewey-sqlite-path"]}")
        
        db = sqlite3.connect(DeweyConfig["dewey-sqlite-path"])
        
        for x in definitions:
            try:
                db.cursor().execute(x)
            except sqlite3.OperationalError as e:
                msg = str(e)
                if msg.startswith("table ") and msg.endswith(" already exists"):
                    print("already exists")
                    pass
                else:
                    raise e

            db.commit()
        db.close()
        print("closed")
    elif DeweyConfig["database-type"] == "MySQL":
        print("creating MySQL")
        print(f"creating new db @{DeweyConfig["mysql-database"]}")

        db = pymysql.connect(host=DeweyConfig["mysql-host"],
                            user=DeweyConfig["mysql-username"],
                            password=DeweyConfig['mysql-password'],
                            #database=DeweyConfig[i[0]],
                            cursorclass=pymysql.cursors.DictCursor)
        
        print("Connected to sql")

        db.cursor().execute(f'CREATE DATABASE {DeweyConfig["mysql-database"]};')
        db.cursor().execute(f'USE {DeweyConfig["mysql-database"]};')
        
        for x in definitions:
            try:
                db.cursor().execute(x)
            except sqlite3.OperationalError as e:
                msg = str(e)
                if msg.startswith("table ") and msg.endswith(" already exists"):
                    print("already exists")
                    pass
                else:
                    raise e

            db.commit()

        db.close()
        print("closed")
    else:
        raise Exception("deweyconfig database-type is not SQLite3 or MySQL")