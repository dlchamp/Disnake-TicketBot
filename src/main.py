from os import listdir

from disnake import Intents
from disnake.ext.commands import Bot

from config import Config


# initialize bot and set elevated intents
intents = Intents.default()
intents.members = True

bot = Bot(case_insensitive=True, intents=intents, test_guilds=[947543739671412878])

@bot.listen()
async def on_ready():
    '''
    discord bot on ready function - invoked when bot is connected
    to discord API and listening for events
    '''
    print(f'{bot.user} is online and connected to Discord.')

def load_cogs(bot):
    '''iterate /cogs and load .py files as bot extensions'''
    for filename in listdir("./cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")


if __name__ == "__main__":
    load_cogs(bot)
    bot.run(Config.BOT_TOKEN)