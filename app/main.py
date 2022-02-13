import os
import json

import config

import disnake
from disnake.ext import commands

# initialize bot and set elevated intents
intents = disnake.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="-", intents=intents)


# load extensions in /cogs
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")


"""
On ready function
- print bot connection status
- print bot user and it's ID
- print configured command prefix
- print number of connected servers and list of servers name (id)
"""


@bot.listen()
async def on_ready():
    print()
    print("--------------------")
    print("Bot has connected to Discord")
    print(f"Bot user: {bot.user}")
    print(f"Bot ID: {bot.user.id}")
    print(f"Command Prefix: {bot.command_prefix}")
    print("--------------------")
    print(f"Connected to {len(bot.guilds)} servers")
    print(f"Connected servers list:")
    for guild in bot.guilds:
        print(f"-- {guild.name}({guild.id})")


if __name__ == "__main__":
    bot.run(config.BOT_TOKEN)
