# Deweybot
Discord bot using discord.py for [ditzykitty](https://www.youtube.com/@DITZYKITTYZZ) & [NIGHTWATCH](https://www.youtube.com/@NIGHTWATCHprod)'s discord server

## Running
Copy `docs/examples/dewey.yaml.example` to the same directory as StartBot.py and fill it out

After filling out the config file, run `tools/init_databases.py` to initalize the databases you set up.

Once everything is set up, run `./StartBot.py` directly or with `python3` or `py`

## Systemd Service
To use the systemd service, fill in:
* `ExecStart` (with the path to StartBot.py)
* `WorkingDirectory` (with the path containing StartBot.py)
* `User` (with your user/the account you want the bot to run as)
  
Then copy it to `/etc/systemd/system/deweybot.service`

Next, run the following commands:
```
sudo systemctl daemon-reload
sudo systemctl enable deweybot
sudo systemctl start deweybot
```

To view logs, run `sudo journalctl -eu deweybot.service`

## Tools
You can run tools from the root of the project (i.e `./tools/convert.py`)
