# Discord Do Not Disturb Bot

I build this Discord Bot  because i was was getting annoyed by people in Voice calls but i didnt want to go in Full Mute because when someone wants to talk to you, you dont hear them because of that this bot creates a Do Not Disturb Voice channel where you can focus on your tasks but when a friend wants to talk to you they can run a command to move you to their channel

## Try the Official Bot

The official bot is already hosted. You can use the Link below to add it to your Discord server. After inviting it, run `/setup` in the server to create the Do Not Disturb channel, Mute Immune role, and Locked In role.

[Invite the official bot to your server](https://discord.com/oauth2/authorize?client_id=1538953537189318788)

## Design Decisions 
- Data Storing: I decided To not use a Database for this Discord Bot instead i used set Names To find Roles and Channels 

- Rate Limiting: Unfortunately i experienced getting Rate Limited Pretty Often For that reason i am Thinking about not letting People Join The call but instead have a button which moves them into it and maybe add a Database which then stores interaction Tokens and send followup Messages when you will get moved instead of sending an Dm 

## Setup

1. Install Python 3.12 or newer.
2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project folder:

```env
# For Normal Use 
Discord_Token=your_discord_bot_token

# For Testing 
Discord_Token_Testing=your_testing_bot_token

# Your Test Server and your User ID copy by enabling Developer Mode in Settings 
Dev_Guild_ID=your_development_server_id
Developer_ID=your_discord_user_id
```

4. In the Discord Developer Portal, enable the **Members**, **Presence**, and **Message Content** intents under the bot settings.
5. Invite the bot with permissions to manage channels and roles, mute and move members, create invites, and send messages.

### Testing Mode

Enable Testing Mode by Creating an Empty testing.txt file

- In Testing Mode the Bot uses 'Discord_Token_Testing' Variable in .env 
- `/restart`, `/shutdown`, and `/undo_setup` are only in available testing mode.

Normally the Bot uses Discord_Token

The Bot sends an Startup Messages to the developer 

## Run

```bash
python Do_Not_Disturb.py
```

## Commands

| Command | Description |
| --- | --- |
| `/setup [category] [default_role]` | Creates the **Do Not Disturb** voice channel, **Mute Immune** role, and **Locked In** role. You can optionally choose a channel category and the role that should be configured as muted in the Do Not Disturb channel. This is useful when `@everyone` cannot join the channel or is already muted in every voice channel, such as when using a verification bot like [SecurityBot](https://securitybot.gg). Admin only. |
| `/undo_setup` | Deletes the Do Not Disturb channel, Mute Immune role, and Locked In role. Testing mode and admin only. |
| `/talk_with @user` |Moves The User to your Voice Channel, Sends a Dm to the User that he will be moved to your Voice Channel in 5 Seconds. When youre Status is Discords Do Not Disturb Status or you have the Locked In Role You will get a Dm with an Invite Link Instead|
| `/lock_in` | Gives You The 'Locked In' Role|
| `/help` | Shows an overview of the bot. Use the dropdown menu to read more about each feature. |
| `/version` | Shows the current version and checks whether the local Git checkout is behind GitHub. |
| `/source` | Shows the source code link and original author information. |
| `/restart` | Closes the bot and creates a restart signal. This is intended to be used with `Restart_Bot.py`. Testing mode only. |
| `/shutdown` | Closes the bot without restarting it. Testing mode only. |

Run `/setup` before using the other bot features.

## Features
| Feature | What It Does |
| --- | --- |

## How To Use

1. An administrator runs `/setup`.
2. Users join **Do Not Disturb** when they do not want to speak or be interrupted.
3. Users with the **Mute Immune** role, such as music bots, can speak in the channel.
4. To contact someone, join another voice channel and run `/talk_with @user`.

To run the optional restart helper instead, use:

```bash
python Restart_Bot.py
```

`Restart_Bot.py` starts the bot and watches for restart signals. Pressing Enter in that window also requests a restart.

## Maintenance Notes

- `/version` and update notifications require a Git checkout with a working `origin` remote.
- The bot's update action uses Linux `systemctl` and is not intended for Windows.
- Runtime logs are written to `discord.log`. The restart system uses `startup.txt`, `restart.txt`, and `shutdown.txt`.
- The `todo` file contains unfinished ideas, such as button-based move requests and channel-based join confirmations.

## Credits

This README was written with AI assistance.
