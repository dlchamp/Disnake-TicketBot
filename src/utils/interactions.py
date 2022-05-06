from disnake import (
    ButtonStyle,
    Interaction,
    Embed,
    TextInputStyle,
    ChannelType,
    ModalInteraction
)
from disnake.ui import (
    View,
    Modal,
    TextInput,
    button,
    Button
)

from utils.db import get_ticket_data, update_ticket_data
from config import Config


class StartTicket(View):
    '''
    Defines the "start ticket" view for Discord
    button interactions
    '''
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot


    @button(label='Start Support', style=ButtonStyle.primary, custom_id='start_support')
    async def start_support(self, button: Button, interaction: Interaction):
        '''Add "start support" button to the ui view'''

        ticket_data = get_ticket_data()

        if interaction.author.id in ticket_data['open_tickets']:
            return await interaction.response.send_message(
                'You already have an open ticket. Please close it before opening another.',
                ephemeral=True
                )


        await interaction.response.send_modal(modal=SupportModal(self.bot))



class SupportModal(Modal):
    '''Adds a modal view to the discord UI'''

    def __init__(self, bot):
        components = [
            TextInput(
                label='Summary',
                placeholder='Describe your issue...',
                custom_id='summary',
                style=TextInputStyle.long,
                min_length=1,
                max_length=250
            )
        ]
        super().__init__(
            title='Create A Support Ticket',
            custom_id = 'create_ticket',
            components=components
        )
        self.bot = bot



    async def callback(self, interaction: ModalInteraction):
        '''
        Modal interaction callback function - invoked when modal
        submitted
        '''
        # get values from modal
        summary = interaction.text_values['summary']
        member = interaction.author
        guild_id = interaction.guild_id
        channel_id = interaction.channel_id

        guild = self.bot.get_guild(guild_id)
        channel = guild.get_channel(channel_id)

        log_channel = guild.get_channel(Config.LOG_CHANNEL)
        admin_role = guild.get_role(Config.ADMIN_ROLE)
        staff_role = guild.get_role(Config.STAFF_ROLE)

        # update the open ticket data
        ticket_data = get_ticket_data()
        ticket_data['open_tickets'].append(member.id)
        update_ticket_data(ticket_data)

        # build the embed for beginning support thread
        embed = Embed(
            title=f"Thanks for requesting support in {guild.name}!",
            description=f"Hey {member.mention}, this is your ticket! Please allow support staff some time to read over your ticket summary and get back to you as soon as they can.\n\n \
            **Remember:**\n \
            - **No one** is obligated to answer you if they feel that you are trolling or otherwise misusing this ticket system.\n\n \
            - **Make sure** to be as clear as possible and provide as many details as you can.\n\n \
            - **Be patient** as we(staff members) have our own lives *outside of Discord* and we tend to get busy most days. We are human, so you should treat us as such!\n\n \
            Abusing/misusing this ticket system may result in punishment that varies from action to action.",
        )
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.add_field(name="Ticket Summary", value=summary, inline=False)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.set_footer(
            text="This ticket may be CLOSED at any time by you, an admin, or support staff."
        )

        # create thread and send beginning message
        new_thread = await channel.create_thread(
            name=f"{str(member)}'s Support Thread",
            type = ChannelType.public_thread
        )

        # send message to new thread - adds Close ticket button to view
        if staff_role == admin_role:
            msg = await new_thread.send(
                    content=f'{member.mention}, {admin_role.mention}',
                    embed=embed,
                    view=CloseTicket(new_thread, member, admin_role, staff_role, log_channel)
                )
        else:
            msg = await new_thread.send(
                    content=f'{member.mention}, {staff_role.mention}, {admin_role.mention}',
                    embed=embed,
                    view=CloseTicket(new_thread, member, admin_role, staff_role, log_channel)
                )

        # pin the embed with close ticket button to refer back later to close ticket if long thead
        await msg.pin()

        # requied interaction response
        await interaction.response.send_message("Your ticket has been created!", ephemeral=True)

        # log new thread in log channel
        if log_channel:
            embed = Embed(
                    title=f'{member.display_name} has opened a support ticket',
                    description=f'[{new_thread.name}](https://discordapp.com/channels/{guild.id}/{new_thread.id})'
                )

            await log_channel.send(embed=embed)




class CloseTicket(View):
    '''Add close ticket button to ui view'''

    def __init__(self, thread, member, admin_role, staff_role, log_channel):
        super().__init__(timeout=None)
        self.member = member
        self.thread = thread
        self.admin = admin_role
        self.staff = staff_role
        self.log = log_channel



    @button(label='Close Ticket', style=ButtonStyle.red)
    async def close_ticket(self, button: Button, interaction: Interaction):
        '''Adds Close ticket button to View and handles button click callback'''
        guild = interaction.guild
        author = interaction.author

        if (
            author == guild.owner
            or author == self.member
            or any(role in [admin_role, staff_role] for role in author.roles)
        ):
            # create embed for dm message
            dm_embed = Embed(
                title=f"You support thread in {guild.name} has been closed.",
                description=f"""If your question has not been answered or your issue is not resolved, please create a new support ticket.\n\n You can use [this link](https://discordapp.com/channels/{guild.id}/{self.thread.id}) to access the archived ticket for future reference.""",
            )
            if guild.icon:
                dm_embed.set_thumbnail(url=guild.icon.url)

            # try to send dm message, if fails, pass
            try:
                await self.member.send(embed=dm_embed)
            except:
                pass

            # stop view, send "thread closed" message, archive thread
            await interaction.response.send_message(
                'This support thread has been closed and archived. If your issue has not been resolved, or another issue arises, please create a new ticket'
                )

            await self.thread.edit(archived=True)
            self.stop()

            # update ticket data and log thread close
            ticket_data = get_ticket_data()
            ticket_data['open_tickets'].remove(self.member.id)
            update_ticket_data(ticket_data)

            if self.log:
                embed = Embed(
                title=f"{author.display_name} has closed a support ticket",
                description=f"[{self.thread.name}](https://discordapp.com/channels/{guild.id}/{self.thread.id})",
                )
                await self.log.send(embed=embed)