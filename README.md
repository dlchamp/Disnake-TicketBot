# Disnake-TicketBot

## Description

A simple to use and manage TicketBot built on the latest version of Disnake.  Let your members start a public support thread to request help with specific issues they need support with.

Features:
- The new discord modal view
- Discord buttons
- DM update support message using the sample.json, uploaded to the bot in a DM that includes the channel ID and message ID for which you wish to update
- Ticket creation and close log message to your configured log channel
- DM user on ticket close with an embed that includes a direct link back to the archived thread for future reference




https://user-images.githubusercontent.com/36091350/154142816-7d43b4be-78e7-4a41-90a4-9fe15f9712c3.mp4





## Bot Usage

- User navigates to your configured help channel and sees the initial support message with a "Start Support" button
- User clicks the button and a discord modal is displayed that allows the user to add up to 500 characters in a "Ticket summary"
- Once submitted, a new public thread is created where the user, and support staff roles are pinged and a "ticket created" message is logged in the log channel
- Ticket is closed when the user, an admin, or support staff Press the "Close" button.
- On ticket close the thread is archived, the user recieves a DM with the notification and a direct link back to the archived ticket, and a "ticket closed" message is logged.

**ADMIN**
- Simply edit the included sample.json file for the message color, title, and description, then go your #help channel and upload the file.  Bot will create the embed and send it to the channel, then delete your message
- To update the embed -
    - Copy the message ID
    - paste it into the message body in #help channel
    - upload the new sample.json
    - send the file.
    - Bot will update the embed and delete your message.



https://user-images.githubusercontent.com/36091350/154142855-071cc58f-8f24-4872-aa2f-5f14e9c1ab36.mp4



## Bot configuration and setup

### Dependencies
* Built on [Python3 - 3.9.7](https://www.python.org/downloads/)
* Disnake version 2.4
* install all dependcies with `python pip install -r requirements.txt`


#### Setting up Discord Bot
1. Login to Discord web - https://discord.com
2. Navigate to Discord Developer Portal - https://discord.com/developers/applications
3. Click *New Application*
4. Give the Appplication a name and *Create*
5. Add image for Discord icon (optional)
7. Keep the default settings for Public Bot - *checked* and Require OAuth2 Code Grant - *unchecked*
8. Add bot image (optional)
9. Copy Token
10. Go to OAuth2 tab
11. Under *Scopes* - Check Bot
12. Under *Bot Permissions* - Admin
13. Copy the generated link and Go to the URL in your browser - Invite Bot to your Discord server

### Configuring the bot
1. Install git
2. Install dependancies with `pip install -r requirements.txt`
3. Edit the .env-sample file and add in your necessary IDs and bot token, rename .env-sample to .env
4. If you do not wish to use an admin AND staff role, just add the same ID to both variables




