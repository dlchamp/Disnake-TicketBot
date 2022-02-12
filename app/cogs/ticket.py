import json
import requests

import disnake
from disnake.ext import commands

import config
from utils.db import get_ticket_data, update_ticket_data


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
max_length = Max character for the textbox (default 500)

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
    Modal interaction callback function

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
            content=member.mention, embed=embed, view=CloseTicket(new_thread, member)
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
                description=f"""If your question has not been answered or your issue is not resolved,
                please create a new support ticket'.\n\n You can use [this link](https://discordapp.com/channels/{inter.guild.id}/{self.thread.id}) to access the archived ticket for future reference.""",
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
        help_channel_id = config.HELP_CHANNEL
        owner_id = config.OWNER_ID
        attachments = message.attachments

        # auto delete pinned "new thread" message
        if message.channel.id == help_channel_id:
            if message.type == disnake.MessageType.thread_created:
                await message.delete()
        """
        check if message is a DM and if it's from the bot owner.
        update the embed message in help channel if all requirements are met

        Requirements:
        Message must be a DM from the bot owner ID (set in env)
        comma separated channel ID, message ID
        if message is for new message, channel ID must be included after :
        uploaded sample.json
        """
        if isinstance(message.channel, disnake.DMChannel):
            if message.author.id == owner_id:
                if message.content.startswith("new"):
                    try:
                        channel_id = message.content.split(":")[1].strip()
                        channel = await self.bot.fetch_channel(channel_id)
                    except:
                        await message.channel.send(
                            'Please make sure your message is in the correct format\nMessage format: "new: channel ID" (upload sample.json), then send'
                        )

                    if len(attachments) == 1:
                        if attachments[0].filename.endswith("json"):
                            url = attachments[0].url
                            response = requests.get(url).json()
                            embed_dict = response["embed"]

                            embed = disnake.Embed.from_dict(embed_dict)
                            await channel.send(
                                content=None, embed=embed, view=TicketButton(self.bot)
                            )
                        else:
                            await message.channel.send(
                                "Please upload only the sample.json file"
                            )
                    else:
                        await message.channel.send(
                            "Please upload only the sample.json file"
                        )

                else:

                    try:
                        message_content = message.content.replace(", ", " ").strip()
                        channel_id, message_id = message_content.split(" ")
                        channel = await self.bot.fetch_channel(channel_id)
                        msg = await channel.fetch_message(message_id)
                    except:
                        await message.channel.send(
                            f"Message should contain the channel ID and message ID in the proper format.\n(Example: 941546832520163328, 941558879744045096 (upload file) then send message."
                        )
                        return

                    if len(attachments) == 1:
                        if attachments[0].filename.endswith("json"):
                            url = attachments[0].url
                            response = requests.get(url).json()
                            embed_dict = response["embed"]

                            embed = disnake.Embed.from_dict(embed_dict)
                            await msg.edit(content=None, embed=embed)
                        else:
                            await message.channel.send(
                                "Please upload only the sample.json file"
                            )
                    else:
                        await message.channel.send(
                            "Please upload only the sample.json file"
                        )


def setup(bot):
    bot.add_cog(Ticket(bot))


print("Ticket extension is loaded")
