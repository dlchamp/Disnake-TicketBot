import json
import disnake
import aiohttp
import asyncio


async def check_attachments(message):

    if len(message.attachments) == 1:
        attachment = message.attachments[0]
        channel = message.channel

        # Confirm uploaded file is the sample.json
        if attachment.filename == "sample.json":
            url = attachment.url

            # Create a async client session and download the json from discord attachment url
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response = await response.json()

            embed = response["embed"]

            # Create the embed object for discord, if fails, return error
            try:
                embed = disnake.Embed.from_dict(embed)
                return embed
            except:
                return "Error"

    return None


async def check_message(message):
    msg_id = message.content

    # check the the ID found in the message content is a valid message within the channel.
    try:
        msg = await message.channel.fetch_message(int(msg_id))
        return msg
    except:
        return "Error"
