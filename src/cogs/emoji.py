from requests import get
from disnake.ext import commands
from disnake import File, HTTPException, utils




class AddEmoji(commands.Cog):
    '''command for adding emoji to guild'''

    def __init__(self, bot):
        self.bot = bot
        self.img_ext = ('png', 'jpg', 'gif')



    @commands.Cog.listener()
    async def on_ready(self):
        '''print to console when cog is loaded'''
        print(f'Cog loaded: {self.qualified_name}')



    @commands.slash_command(name='add_emoji')
    @commands.has_permissions(manage_emojis=True)
    async def add_emoji(self, inter, link: str, name: str):
        '''
        Upload an emoji to the guild

        Parameters
        ----------
        link: Discord message link (copy message link)
        name: Name of the emoji
        '''

        # defer interaction while image being saved
        await inter.response.defer(ephemeral=True)

        guild = inter.guild

        # split link into guild, channel, and message IDs
        link_split = link.split('/')
        channel = guild.get_channel(int(link_split[5]))
        msg = await channel.fetch_message(int(link_split[6]))

        # get attachments from message
        if msg.attachments:
            a = msg.attachments[0]
            r = get(a.url)
            img = r.content
            # create the emoji in the guild
            try:
                new_emoji = await guild.create_custom_emoji(
                        name=name,
                        image=img,
                        reason=f'Added by {inter.author.name} via command'
                    )

            except HTTPException as error:

                if "256.0 kb" in str(error):
                    return await inter.edit_original_message(content=f'Image file too large (Max: 256 kb)')

                return await inter.edit_original_message(content=f'Error: Could not add the custom emoji to this server.')

            return await inter.edit_original_message(content=f'Custom emoji created: {new_emoji.name}')

        await inter.edit_original_message(content=f'Error: Link did not include a message that had a supported image.')


    @commands.slash_command(name='delete_emoji')
    @commands.has_permissions(manage_emojis=True)
    async def add_emoji(self, inter, emoji: str):
        '''
        Delete the target emoji from the guild

        Parameters
        ----------
        emoji: Name of the emoji
        '''
        guild = inter.guild

        # get target emoji by name
        emoji = utils.get(guild.emojis, name=emoji)

        if emoji:
            await guild.delete_emoji(emoji, reason=f'Deleted by {inter.author.name} via command')
            return await inter.response.send_message(f'Target emoji deleted', ephemeral=True)

        await inter.response.send_message(f'No emoji with that name was found', ephemeral=True)


def setup(bot):
    bot.add_cog(AddEmoji(bot))