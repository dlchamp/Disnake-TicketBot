import json
import requests

import disnake
from disnake.ext import commands

from config import Config
from utils.db import get_ticket_data, update_ticket_data
from utils.check import check_attachments, check_message
from utils.interactions import StartTicket


class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # persistent listener for Start Support button
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(StartTicket(self.bot))

    """
    on message listener
    removes the auto-pinned message when a new thread is created

    Listens for DMs from bot owner to update the help channel embed message
    takes a channel ID, message ID message, splits the message and fetches the channel and message

    Params:
    message - the message object

    Message must include a comma separated channel ID, message ID, and the uploaded sample.json file
    """

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot and message.type != disnake.MessageType.thread_created:
            return

        guild = message.guild
        owner = guild.owner
        channel = message.channel
        help_channel = guild.get_channel(Config.HELP_CHANNEL)
        admin_role = guild.get_role(Config.ADMIN_ROLE)
        help_channel = await self.bot.fetch_channel(Config.HELP_CHANNEL)

        if channel == help_channel:
            # auto delete the "new thead" message
            if message.type == disnake.MessageType.thread_created:
                await message.delete()
                return

            if message.author == owner or admin_role in message.author.roles:
                """
                Add new embed to the channel - only attach file with an empty message
                file must be the edited sample.json file
                """
                if message.content == "":
                    """
                    Message content is empty - new embed
                    check for correct file criteria, must be 1 file
                    must be the sample.json
                    """
                    embed = await check_attachments(message)

                    if embed == "Error":
                        await channel.send(
                            "Please check the sample.json for proper formatting.",
                            delete_after=5,
                        )
                    elif embed is None:
                        await channel.send(
                            "No supported file was uploaded.", delete_after=5
                        )
                    else:
                        await channel.send(embed=embed, view=StartTicket(self.bot))
                    await message.delete()

                else:
                    """
                    Message content is not empty, should be a message ID only
                    Check attachments, and check message ID to confirm it's a message
                    If no errors, update embed in channel
                    """
                    msg = await check_message(message)
                    embed = await check_attachments(message)

                    if msg == "Error":
                        await channel.send(
                            f"No channel with that ID was found", delete_after=5
                        )
                    else:
                        if embed is None:
                            await channel.send(
                                "No supported file was uploaded.", delete_after=5
                            )
                        elif embed == "Error":
                            await channel.send(
                                "Please check the sample.json for formatting issues.",
                                delete_after=5,
                            )
                        else:
                            await msg.edit(content=None, embed=embed)
                    await message.delete()

    # command for downloading sample.json - requires admin or owner
    @commands.command(aliases=["sample", "s", "json"])
    async def download_sample(self, ctx):
        guild = ctx.guild
        owner = guild.owner
        member = ctx.author
        admin_role = guild.get_role(config.ADMIN_ROLE)

        if member == owner or admin_role in member.roles:
            await ctx.send(f"Check your DM for the sample file.", delete_after=5)
            await member.send(file=disnake.File("../sample.json"))
        else:
            await ctx.send(
                f"You do not have permission to use this command.", delete_after=5
            )


def setup(bot):
    bot.add_cog(Ticket(bot))


print("Ticket extension is loaded")
