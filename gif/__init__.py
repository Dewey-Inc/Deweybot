# Code i stole from stackoverflow because mine didn't work
from math import ceil

from PIL import Image, ImageDraw, ImageSequence, ImageFont, ImageOps
import io, textwrap

newGif = Image.open('./gif/base.gif')
oldGif = Image.open('./gif/old.gif')
font = ImageFont.truetype('./gif/Futura Extra Bold Condensed.otf', 30)

def isLonger(text):
    text = textwrap.fill(text, 20)
    return text.count("\n") < 9

def baseImg(text):
    im = newGif if isLonger(text) else oldGif
    text = textwrap.fill(text, 20)
    d = ImageDraw.Draw(Image.new("RGB", (0,0))) # need to make a temp image to measure the text size (stupid)
    textSize = d.multiline_textbbox((0, 0), font=font, text=text, spacing=15)

    frame = Image.new("RGB", (max(ceil(textSize[2]) + 24, im.width), ceil(textSize[3]) + 24), (255,255,255))
    d = ImageDraw.Draw(frame)
    d.multiline_text((frame.width/2,12), text, (0,0,0), font, "ma", align="center", spacing=15)

    return ImageOps.contain(frame, (im.width, -1))


def gen(text):
    im = newGif if isLonger(text) else oldGif
    textImg = baseImg(text)

    frames = []
    # Loop over each frame in the animated image
    for frame in ImageSequence.Iterator(im):
        b = io.BytesIO()
        frame.save(b, format="GIF")
        old_frame = Image.open(b)
        frame = Image.new("RGB", (im.width, im.height + textImg.height), (255, 255, 255))

        frame.paste(textImg, (0, 0))
        frame.paste(old_frame, (0, textImg.height))

        frames.append(frame)

    buffer = io.BytesIO()
    duration = 20 if isLonger(text) else 40
    frames[0].save(buffer, format="GIF", save_all=True, append_images=frames[1:], loop=0, duration=duration)
    buffer.seek(0)
    return buffer
