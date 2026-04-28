#! /usr/bin/env python3

import json
import sqlite3
import pymysql
import argparse
import datetime

parser = argparse.ArgumentParser("export_to_json.py",)
parser.add_argument("type", help="sqlite3 or pymysql", type=str)
parser.add_argument("db", help="Database file/host", type=str)
parser.add_argument("export", help="Filename to export to", type=str)
parser.add_argument("-u", help="Database username (only required on pymysql)", type=str, required=False)
parser.add_argument("-p", help="Database password (only required on pymysql)", type=str, required=False)
args = parser.parse_args()

if args.type == "sqlite3":

    db = sqlite3.connect(args.db)
    cursor = db.cursor()
    
    map = {
        "INFO": {
            "timestamp": datetime.datetime.now().timestamp()
        }
    }

    tables = cursor.execute("pragma table_list;").fetchall()
    for table in tables:
        print(f"In {table[1]}")
        rows = cursor.execute(f"pragma table_info({table[1]});").fetchall()
        rowmap = {}

        for x in rows:
            rowmap[x[1]] = {
                "index": x[0],
                "name": x[1],
                "type": x[2],
                "notnull": x[3],
                "dflt_value": x[4],
                "pk": x[5],
                "data": cursor.execute(f"SELECT {x[1]} FROM {table[1]};").fetchall()
            }
            map[table[1]] = rowmap

    with open(args.export, "w") as f:
        json.dump(map,f)
elif args.type == "pymysql":
    raise Exception("pymysql not implemented")
else:
    parser.print_usage()