import json
import requests

import disnake
from disnake.ext import commands

import config
from utils.db import get_ticket_data, update_ticket_data
from utils.check import check_attachments, check_message


class TicketButton(disnake.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    """
    Start support button interaction for TicketButton view

    Button Params:
    label - button label
    style - button style (primary = discord blurple color)

    Function: support_button
    Check if interaction member already has an open ticket in tickets.json.
    If not exists, start new ticket process and add member ID to json

    Returns discord ui Modal to take in ticket summary

    Params:
    button - disnake ui Button
    interaction - disnake Interaction
    """

    @disnake.ui.button(
        label=f"Start Support",
        style=disnake.ButtonStyle.primary,
        custom_id="start_support",
    )
    async def support_button(
        self, button: disnake.ui.Button, interaction: disnake.Interaction
    ):
        # get open ticket list to check if member alredy has an open ticket
        ticket_data = get_ticket_data()

        if interaction.author.id in ticket_data["open_tickets"]:
            await interaction.response.send_message(
                f"You already have an open ticket. Please close it before starting a new ticket",
                ephemeral=True,
            )
            return
        await interaction.response.send_modal(modal=SupportModal(self.bot))


"""
Modal view (pop out window)

Modal View components
Params:
label - text box title
placeholder - Summary box text, gets replaced when user starts typing
style = Textbox style (long input)
min_length - Required minimum character count in text box
max_length = Max character for the text box

Modal view
Params:
title - Modal window title
custom_id - give the view a custom ID
components - modal view components
"""


class SupportModal(disnake.ui.Modal):
    def __init__(self, bot):
        components = [
            disnake.ui.TextInput(
                label="Summary",
                placeholder="Provide some info for your support ticket",
                custom_id="summary",
                style=disnake.TextInputStyle.long,
                min_length=1,
                max_length=500,
            )
        ]
        super().__init__(
            title="Create a Support Ticket",
            custom_id="create_ticket",
            components=components,
        )
        self.bot = bot

    """
    Modal interaction callback

    Gets the open tickets from tickets.json, checks modal interaction author against the returned list
    if user ID exists in list, send ephemeral message, do not create thread/ticket
    Otherwise, add user ID to list and update the ticket.json
    Create new ticket/thread - Params: title, type: public

    Params:
    inter - disnake Interaction
    """

    async def callback(self, inter: disnake.ModalInteraction):
        ticket_summary = inter.text_values["summary"]
        member = inter.author
        guild_id = inter.guild_id
        channel_id = inter.channel_id

        guild = self.bot.get_guild(guild_id)
        log_channel = guild.get_channel(config.LOG_CHANNEL)
        channel = guild.get_channel(channel_id)
        staff_role = guild.get_role(config.STAFF_ROLE)
        # update list of current open tickets
        ticket_data = get_ticket_data()
        ticket_data["open_tickets"].append(member.id)
        update_ticket_data(ticket_data)

        # create the thread and initial embed message
        new_thread = await channel.create_thread(
            name=f"{guild.name} Help - {member}", type=disnake.ChannelType.public_thread
        )

        embed = disnake.Embed(
            title=f"Thanks for requesting support in {inter.guild.name}!",
            description=f"Hey {member.mention}, this is your ticket! Please allow support staff some time to read over your ticket summary and get back to you as soon as they can.\n\n \
            **Remember:**\n \
            - **No one** is obligated to answer you if they feel that you are trolling or otherwise misusing this ticket system.\n\n \
            - **Make sure** to be as clear as possible and provide as many details as you can.\n\n \
            - **Be patient** as we(staff members) have our own lives *outside of Discord* and we tend to get busy most days. We are human, so you should treat us as such!\n\n \
            Abusing/misusing this ticket system may result in punishment that varies from action to action.",
        )
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.add_field(name="Ticket Summary", value=ticket_summary, inline=False)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
        embed.set_footer(
            text="This ticket may be CLOSED at any time by you, an admin, or support staff."
        )
        # send message to new thread, add CloseTicket interaction view button
        # Params: new_thread, member
        await new_thread.send(
            content=f'{member.mention}, {staff_role.mention}', embed=embed, view=CloseTicket(new_thread, member)
        )
        # Required interaction response
        await inter.send(f"Your ticket has been created.", ephemeral=True)

        # send log embed to log channel
        embed = disnake.Embed(
            title=f"{member.display_name} has opened a support ticket",
            description=f"[{new_thread.name}](https://discordapp.com/channels/{guild.id}/{new_thread.id})",
        )
        await log_channel.send(embed=embed)


"""
Close ticket interaction button view
Params: thread, member
"""


class CloseTicket(disnake.ui.View):
    def __init__(self, thread, member):
        super().__init__(timeout=None)
        self.member = member
        self.thread = thread

    """
    Interaction button for closing ticket/archiving thread
    Params: style: button color (red), custom_id: button id

    close_ticket function
    Pressing button will archive the thread (close the ticket), send a log message to log channel
    displaying who closed the ticket

    Params:
    button - interaction button
    interaction - interaction callback when button is clicked
    """

    @disnake.ui.button(label=f"Close", style=disnake.ButtonStyle.red, custom_id="close")
    async def close_ticket(self, button: disnake.ui.Button, inter: disnake.Interaction):
        guild = inter.guild
        admin_role_id = config.ADMIN_ROLE
        staff_role_id = config.STAFF_ROLE
        admin_role = guild.get_role(admin_role_id)
        staff_role = guild.get_role(staff_role_id)
        log_channel = guild.get_channel(config.LOG_CHANNEL)

        """
        Close ticket button can only be used by:
        member that created the ticket
        members with admin role
        members with staff role
        """
        if (
            inter.author == self.member
            or inter.author == guild.owner
            or admin_role in inter.author.roles
            or staff_role in inter.author.roles
        ):

            embed = disnake.Embed(
                title=f"You support thread in {inter.guild.name} has been closed.",
                description=f"""If your question has not been answered or your issue is not resolved, please create a new support ticket.\n\n You can use [this link](https://discordapp.com/channels/{inter.guild.id}/{self.thread.id}) to access the archived ticket for future reference.""",
            )
            if inter.guild.icon:
                embed.set_thumbnail(url=inter.guild.icon.url)

            await self.member.send(embed=embed)
            await inter.response.send_message(
                "This support thread has been closed.  If your issue has not been solved, please create a new ticket."
            )
            await self.thread.edit(archived=True)
            # disable button after click
            self.stop()

            # remove member from list of currently open tickets
            ticket_data = get_ticket_data()
            ticket_data["open_tickets"].remove(self.member.id)
            update_ticket_data(ticket_data)

            # send log embed to log channel
            embed = disnake.Embed(
                title=f"{inter.author.display_name} has closed a support ticket",
                description=f"[{self.thread.name}](https://discordapp.com/channels/{inter.guild.id}/{self.thread.id})",
            )
            await log_channel.send(embed=embed)


class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # persistent listener for Start Support button
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TicketButton(self.bot))

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
        help_channel = await self.bot.fetch_channel(config.HELP_CHANNEL)

        if message.channel == help_channel:
            guild = message.guild
            owner = guild.owner
            admin_role = guild.get_role(config.ADMIN_ROLE)
            '''
            Add new embed with attached "Start Support" button or
            edit current embed

            Check if the message comes from an Admin role from the guild owner
            '''
            if (
                message.author == owner or
                admin_role in message.author.roles
                ):

                '''
                Add new embed to the channel - only attach file with an empty message
                file must be the edited sample.json file
                '''
                if message.content == '':
                    '''
                    Message content is empty - new embed
                    check for correct file criteria, must be 1 file
                    must be the sample.json
                    '''
                    embed = await check_attachments(message)

                    if embed == 'Error':
                        await channel.send('Please check the sample.json for proper formatting.', delete_after=5)
                        return
                    await channel.send(embed=embed, view=TicketButton(self.bot))
                    await message.delete()

                else:
                    '''
                    Message content is not empty, should be a message ID only
                    Check attachments, and check message ID to confirm it's a message
                    If no errors, update embed in channel
                    '''
                    msg = await check_message(message)
                    embed = await check_attachments(message)

                    if not msg == 'Error':
                        if not embed == 'Error':
                            await msg.edit(content=None, embed=embed)
                        else:
                            await channel.send('Please check the sample.json', delete_after=5)
                    else:
                        await channel.send('No message with that ID was found.', delete_after=5)

                    await message.delete()






def setup(bot):
    bot.add_cog(Ticket(bot))


print("Ticket extension is loaded")
