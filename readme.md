# Discord Do Not Disturb Bot

A Discord bot that creates a **Do Not Disturb** voice channel. Users can join the channel when they do not want to be disturbed. They cannot speak there unless they have the **Mute Immune** role.

When someone uses `/talk_with`, the bot can move a user from the Do Not Disturb channel to the caller's voice channel. If the user has their Discord status set to Do Not Disturb, the bot sends them a private message instead.

## Setup

1. Install Python 3.
2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project folder:

```env
AFK_Voice_Token=your_discord_bot_token
```

4. In the Discord Developer Portal, enable the **Members**, **Presence**, and **Message Content** intents under the bot settings.
5. Invite the bot with permissions to manage channels and roles, mute and move members, create invites, and send messages.

The bot is currently configured for the development server in the Python file. Slash commands will not appear in other servers unless the guild configuration is changed.

## Run

```bash
python Do_Not_Disturb.py
```

## Commands

| Command | Description |
| --- | --- |
| `/setup [category]` | Creates the **Do Not Disturb** voice channel and **Mute Immune** role. You can optionally choose a category for the channel. Admin only. |
| `/undo_setup` | Deletes the Do Not Disturb channel and Mute Immune role. Use this only when you want to remove the bot's setup. Admin only. |
| `/talk_with @user` | Requires you to be in a voice channel. Moves the selected user out of Do Not Disturb and into your channel. If their status is DND, sends them a private message with an invite instead. |
| `/help` | Shows an overview of the bot. Use the dropdown menu to read more about each feature. |
| `/restart` | Closes the bot and creates a restart signal. This is intended to be used with `Restart_Bot.py`. Dev only. |
| `/shutdown` | Closes the bot without restarting it. Dev only. |

Run `/setup` before using the other bot features.

## How To Use

1. An administrator runs `/setup`.
2. Users join **Do Not Disturb** when they do not want to speak or be interrupted.
3. Users with the **Mute Immune** role, such as music bots, can speak in the channel.
4. To contact someone, join another voice channel and run `/talk_with @user`.

To run the optional restart helper instead, use:

```bash
python Restart_Bot.py
```