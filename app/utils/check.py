import json
import disnake
import aiohttp
import asyncio


async def check_attachments(message):
    attachment = message.attachments[0]
    channel = message.channel
    if attachment.filename == 'sample.json':
        url = attachment.url
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response = await response.json()

        embed = response['embed']

        try:
            embed = disnake.Embed.from_dict(embed)
            return embed
        except:
            return 'Error'



async def check_message(message):
    msg_id = message.content

    try:
        msg = await message.channel.fetch_message(int(msg_id))
        return msg
    except:
        return 'Error'





