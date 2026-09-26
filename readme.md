# Discord Do Not Disturb Bot

This Discord bot creates a **Do Not Disturb** voice channel for focused work. Friends can still request to talk with someone without requiring them to leave Discord or disable all notifications.

## Try the Official Bot

The official bot is already hosted. Use the link below to add it to a Discord server, then run `/setup` to create the Do Not Disturb channel, Mute Immune role, and Locked In role.

[Invite the official bot to your server](https://discord.com/oauth2/authorize?client_id=1538953537189318788)

## Setup

1. Install Python 3.14 or newer.
2. Install [uv](https://docs.astral.sh/uv/).
3. Install the project dependencies:

```shell
uv sync
```

4. Create a `.env` file in the project folder:

```env
# Used when testing=false
Discord_Token=your_discord_bot_token

# Used when testing=true
Discord_Token_Testing=your_testing_bot_token

# Development server ID. Enable Discord Developer Mode to copy IDs.
Dev_Guild_ID=your_development_server_id

# Channel where changelog messages are sent
Changelog_Channel_ID=your_changelog_channel_id

# Set to true for testing mode or false for normal operation
testing=false
```

5. In the Discord Developer Portal, enable the **Members**, **Presence**, and **Message Content** intents under the bot settings.
6. Invite the bot with permissions to manage channels and roles, mute and move members, create invites, and send messages.

### Testing Mode

Set `testing=true` in `.env` to enable testing mode.

- Testing mode uses `Discord_Token_Testing` and syncs commands to `Dev_Guild_ID`.
- `/undo_setup` is available in testing mode only. `/undo_setup` Deletes the Do Not Disturb channel, Mute Immune role, and Locked In role, admin only.

Set `testing=false` for normal operation. The bot then uses `Discord_Token` and syncs commands globally.

The [`basicdiscordbot`](https://github.com/Gladiatorsarius/BasicDiscordBot) integration provides the bot's maintenance features, including `/info` and automatic pull/restart behavior. `Changelog_Channel_ID` tells the integration where changelog messages should be sent.

## Run

```bash
uv run Do_Not_Disturb.py
```

You can also run the script with the selected Python environment:

```bash
python Do_Not_Disturb.py
```

## Commands

| Command | Description |
| --- | --- |
| `/setup [category] [default_role]` | Creates the **Do Not Disturb** voice channel, **Mute Immune** role, and **Locked In** role. `category` optionally selects the channel category. `default_role` selects the role that receives the channel's default connect and muted permissions. This is useful when `@everyone` cannot join the channel or is already muted in every voice channel, such as when using a verification bot like [SecurityBot](https://securitybot.gg). Admin only. |
| `/talk_with @user` | Requires you to be in a voice channel. A user in Do Not Disturb receives a DM and is moved after five seconds. Users with DND status or the Locked In role receive a DM with an invite instead of being moved. |
| `/lock_in` | Toggles the Locked In role for yourself. Users with this role cannot be moved by `/talk_with`. |
| `/help` | Shows an overview of the bot. Use the dropdown menu to read more about each feature. |
| `/info` | Shows information provided by the `basicdiscordbot` integration. |

Run `/setup` before using the other bot features.

## How To Use

1. An administrator runs `/setup`.
2. Users join **Do Not Disturb** when they do not want to speak or be interrupted.
3. Users with the **Mute Immune** role, such as music bots, can speak in the channel.
4. To contact someone, join another voice channel and run `/talk_with @user`.


## Maintenance Notes

- The project uses `pyproject.toml` and `uv.lock` for dependency management.
- The bot writes runtime logs to `discord.log`.
- The [`basicdiscordbot`](https://github.com/Gladiatorsarius/BasicDiscordBot) update integration uses a Git checkout with an `origin` remote and may use Linux `systemctl` for service restarts.
- The `todo` file contains unfinished ideas, such as button-based move requests and channel-based join confirmations.
- Version `2.0.0` is the current rewrite using the `basicdiscordbot` integration. See [CHANGELOG.md](CHANGELOG.md) for release notes.

## Credits

This README was written with AI assistance.
