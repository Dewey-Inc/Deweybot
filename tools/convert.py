#! /usr/bin/env python3
import glob
import time
from PIL import Image, ImageSequence, ImageOps


# loading dewey config to get path of files

from yaml import load,Loader

with open("dewey.yaml", "r") as f:
    DeweyConfig = load(stream=f, Loader=Loader)

if DeweyConfig["file-saving"] != "Local":
    print("this tool doesn't SUPPORT that (filesaving must be local).")
    exit(-1)

path = DeweyConfig["image-save-path"]



files = []

# load all of the registered card's image file paths
if DeweyConfig["database-type"] == "SQLite3":
    import sqlite3

    db = sqlite3.connect(database=DeweyConfig["dewey-sqlite-path"])
    cursor = db.cursor()
    cursor.execute("SELECT filename FROM gacha")
    data = cursor.fetchall()
    for i in data:
        files.append(path + ("/" if path[len(path)-1] != "/" else "") + i[0])

elif DeweyConfig["database-type"] == "MySQL": # NOT TESTED
    import pymysql
    print ("not tested with mysql btw")

    db = pymysql.connect(host=DeweyConfig["mysql-host"],
                user=DeweyConfig["mysql-username"],
                password=DeweyConfig['mysql-password'],
                database=DeweyConfig["mysql-database"])
    cursor = db.cursor()
    cursor.execute(query="SELECT filename FROM gacha")
    data = cursor.fetchall()
    for i in data:
        files.append(path + ("/" if path[len(path)-1] != "/" else "") + i[0])

else:
    # it's like whatever
    files = glob.glob(f"{path}/CARD-*")
    



total_start = time.time()
failures: list[tuple[str, Exception]] = []

for file in files:
    filename = file.split("/")[-1].split(".")[0]
    print(f"working on {filename}... ", end="")

    start = time.time()

    try:
        img = Image.open(file)
        small = []
        inv_frames = []
        inv_small = []
        durations = []

        for frame in ImageSequence.Iterator(img):
            small.append(ImageOps.contain(frame, (350, 500)))
            inv_frames.append(ImageOps.invert(frame.convert("RGB")))
            inv_small.append(ImageOps.contain(inv_frames[-1], (350, 500)))
            durations.append(frame.info.get("duration", 40))
        
        ext = "png"
        if len(small) > 1:
            ext = "gif"
            small[0].save(
                f"{path}/small/{filename}.{ext}",format="GIF",save_all=True,append_images=small[1:],loop=0,durations=durations,disposal=2
            )
            inv_frames[0].save(
                f"{path}/E{filename}.{ext}",format="GIF",save_all=True,append_images=inv_frames[1:],loop=0,durations=durations
            )
            inv_small[0].save(
                f"{path}/small/E{filename}.{ext}",format="GIF",save_all=True,append_images=inv_small[1:],loop=0,durations=durations
            )
        else:
            small[0].save(f"{path}/small/{filename}.{ext}", format="png")
            inv_frames[0].save(f"{path}/E{filename}.{ext}", format="png")
            inv_small[0].save(f"{path}/small/E{filename}.{ext}", format="png")
        filename += f".{ext}"

    except Exception as e:
        failures.append((file, e))
        print("\x1b[31mfailed... \x1b[0m", end="") # i want it to be red.... to stick out....
    finally:
        print(f"took {round(number=time.time()-start,ndigits=2)}s")

if len(failures) > 0:
    import traceback
    for i in failures:
        print(f"File {i[0]}")
        traceback.print_exception(i[1])
        print("\n")

print("Done!")
print(f"total {round(number=time.time()-total_start,ndigits=2)}s")