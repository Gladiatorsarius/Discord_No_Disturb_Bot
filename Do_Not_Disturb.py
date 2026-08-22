import discord
import os
from dotenv import load_dotenv
from discord.ext import commands, tasks
import logging
from discord import app_commands
import types

load_dotenv()
discord_token = os.getenv('Discord_Token')


handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

Developer_ID = 1130514544960225402
Dev_Guild_ID = discord.Object(id=1537433277445574676)

In_Prod = False  # Set to True when deploying to production

class Client(commands.Bot):
    async def setup_hook(self):
        try:
            if In_Prod:
                synced_Global = await self.tree.sync()
                synced_Guild = await self.tree.sync(guild=Dev_Guild_ID)
                print(f"Synced {len(synced_Global)} global commands and {len(synced_Guild)} guild commands.")
            else:
                self.tree.copy_global_to(guild=Dev_Guild_ID)
                synced_guild = await self.tree.sync(guild=Dev_Guild_ID)
                print(f"Synced {len(synced_guild)} commands to the guild {Dev_Guild_ID.id}.")
                self.tree.clear_commands(guild=None)
                await self.tree.sync()
                print("Cleared global commands.")
        except Exception as e:
            print(f"Error syncing commands: {e}")
        

    async def on_ready(self):
        print(f'Logged in as {self.user.name}')
        if not status_task.is_running():
            status_task.start()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
client = Client(intents=intents ,command_prefix='!')

@client.tree.command(name="restart", description="Restarts the bot" , guild=Dev_Guild_ID)
async def restart(interaction: discord.Interaction):
    await interaction.response.send_message("Restarting the bot...", ephemeral=True)
    print("/restart command received.Shutting down...")
    with open("startup.txt", "w") as f:
        pass
    await interaction.client.close()

@client.tree.command(name="shutdown", description="Shuts down the bot", guild=Dev_Guild_ID)
async def shutdown(interaction: discord.Interaction):
    await interaction.response.send_message("Shutting down the bot...", ephemeral=True)
    print("/shutdown command received. Shutting down...")
    await client.close()

@tasks.loop(seconds=1)
async def status_task():
    if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "shutdown.txt")):
        print("Shutdown signal received. Shutting down...")
        os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)), "shutdown.txt"))
        await client.close()
    if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "restart.txt")):
        print("Restart signal received. Restarting...")
        os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)), "restart.txt"))
        with open("startup.txt", "w") as f:
            pass
        await client.close()

@status_task.before_loop
async def before_status_task():
    await client.wait_until_ready()

@client.event
async def on_voice_state_update(member, before, after):
    Mute_Immune_Role = discord.utils.get(after.channel.guild.roles, name="Mute Immune")
    if member.get_role(Mute_Immune_Role.id):
        if after.channel is not None and after.channel.name == "Do Not Disturb":
            await member.edit(mute=False)
        return

    Do_Not_Disturb_Channel = discord.utils.get(after.channel.guild.voice_channels, name="Do Not Disturb")

    if after.channel == Do_Not_Disturb_Channel:
        if member.guild_permissions.administrator:
            await member.edit(mute=True)
    
    elif after.channel != Do_Not_Disturb_Channel:
        if member.guild_permissions.administrator:
            await member.edit(mute=False)


@client.tree.command(name="setup" , description="Sets up the Bot" )
@app_commands.checks.has_permissions(administrator=True)
async def setup(interaction: discord.Interaction, category: discord.CategoryChannel = None):
    setup_progress = "Setting up the bot..."
    do_not_disturb_channel_message = "Waiting for previous steps to complete..."
    do_not_disturb_permission_everyone_message = "Waiting for previous steps to complete..."
    do_not_disturb_permission_mute_immune_message = "Waiting for previous steps to complete..."
    mute_immune_role_message = "Waiting for previous steps to complete..."


    async def update_embed(step_message):
        nonlocal setup_progress
        if step_message == 4:
            setup_progress = "Setup completed successfully!"
        embed = discord.Embed(title="Setup Progress", description=setup_progress, color=discord.Color.blue())
        embed.add_field(name="Mute Immune Role", value=f"{mute_immune_role_message}", inline=False)
        embed.add_field(name="Do Not Disturb Channel", value=f"{do_not_disturb_channel_message}", inline=False)
        embed.add_field(name="Do Not Disturb Permissions", value=f"{do_not_disturb_permission_everyone_message}", inline=False)
        embed.add_field(name="Mute Immune Permissions", value=f"{do_not_disturb_permission_mute_immune_message}", inline=False)
        embed.set_footer(text=f"{step_message}/4 Steps completed.")
        return embed

    await interaction.response.send_message(embed=await update_embed(0), ephemeral=True)


    mute_immune_role_message = "Checking 'Mute Immune' role..."
    await interaction.edit_original_response(embed=await update_embed(0))
    
    Mute_Immune_Role = discord.utils.get(interaction.guild.roles, name="Mute Immune")
    if Mute_Immune_Role is None:
        await interaction.guild.create_role(name="Mute Immune")
        Mute_Immune_Role = discord.utils.get(interaction.guild.roles, name="Mute Immune")
        mute_immune_role_message = f"Created {Mute_Immune_Role.mention} role. :white_check_mark: "
    else:
        mute_immune_role_message = f"{Mute_Immune_Role.mention} role exists. :white_check_mark: "


    do_not_disturb_channel_message = "Checking if 'Do Not Disturb channel' exists :arrows_clockwise: ... "
    await interaction.edit_original_response(embed=await update_embed(1))

    Do_Not_Disturb_Channel = discord.utils.get(interaction.guild.voice_channels, name="Do Not Disturb")
    if Do_Not_Disturb_Channel is None:
        await interaction.guild.create_voice_channel(name ="Do Not Disturb" , category=category)
        Do_Not_Disturb_Channel = discord.utils.get(interaction.guild.voice_channels, name="Do Not Disturb")
        do_not_disturb_channel_message = f"Created {Do_Not_Disturb_Channel.mention} channel. {"As Uncategorized Voice Channel" if category is None else f"Under {category.name}"} :white_check_mark: "

        do_not_disturb_permission_everyone_message = f"Setting 'Do Not Disturb' channel permissions for {interaction.guild.default_role.mention} :arrows_clockwise: ..."
        await interaction.edit_original_response(embed=await update_embed(2))

        await Do_Not_Disturb_Channel.set_permissions(interaction.guild.default_role, connect=True, speak=False)
        do_not_disturb_permission_everyone_message = f"Set 'Do Not Disturb' channel permissions for {interaction.guild.default_role.mention} to not speak. :white_check_mark: "

        do_not_disturb_permission_mute_immune_message = f"Setting 'Do Not Disturb' channel permissions for {Mute_Immune_Role.mention} :arrows_clockwise: ..."
        await interaction.edit_original_response(embed=await update_embed(3))

        await Do_Not_Disturb_Channel.set_permissions(Mute_Immune_Role, speak=True)
        do_not_disturb_permission_mute_immune_message = f"Set 'Do Not Disturb' channel permissions for {Mute_Immune_Role.mention} to speak. :white_check_mark: "
        await interaction.edit_original_response(embed=await update_embed(4))

    else:
        do_not_disturb_channel_message = f"{Do_Not_Disturb_Channel.mention} channel exists. :white_check_mark: "
        do_not_disturb_permission_everyone_message = f"Checking  'Do Not Disturb' channel permissions for {interaction.guild.default_role.mention} :arrows_clockwise: ..."
        await interaction.edit_original_response(embed=await update_embed(2))
        if Do_Not_Disturb_Channel.permissions_for(interaction.guild.default_role).speak is not False:
            await Do_Not_Disturb_Channel.set_permissions(interaction.guild.default_role, connect=True, speak=False)
            do_not_disturb_permission_everyone_message = f"Set 'Do Not Disturb' channel permissions for {interaction.guild.default_role.mention} to not speak. :white_check_mark: "
        else:
            do_not_disturb_permission_everyone_message = f"'Do Not Disturb' channel permissions for {interaction.guild.default_role.mention} are already set to not speak. :white_check_mark: "

        do_not_disturb_permission_mute_immune_message = f"Checking 'Do Not Disturb' channel permissions for {Mute_Immune_Role.mention} :arrows_clockwise: ..."
        await interaction.edit_original_response(embed=await update_embed(3))
        if Do_Not_Disturb_Channel.permissions_for(Mute_Immune_Role).speak is not True:
            await Do_Not_Disturb_Channel.set_permissions(Mute_Immune_Role, speak=True)
            do_not_disturb_permission_mute_immune_message = f"Set 'Do Not Disturb' channel permissions for {Mute_Immune_Role.mention} to speak. :white_check_mark: "
        else:
            do_not_disturb_permission_mute_immune_message = f"'Do Not Disturb' channel permissions for {Mute_Immune_Role.mention} are already set to speak. :white_check_mark: "
        await interaction.edit_original_response(embed=await update_embed(4))

@setup.error
async def setup_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You do not have permission to use this command.\nPls ask an administrator to set up the bot.", ephemeral=True)


# @client.tree.command(name="undo_setup", description="Undoes the setup of the bot")
# @app_commands.checks.has_permissions(administrator=True)
# async def undo_setup(interaction: discord.Interaction):
#     await interaction.response.send_message("Undoing setup...", ephemeral=True)
#     Do_Not_Disturb_Channel = discord.utils.get(interaction.guild.voice_channels, name="Do Not Disturb")
#     Mute_Immune_Role = discord.utils.get(interaction.guild.roles, name="Mute Immune")
#     if Do_Not_Disturb_Channel is not None:
#         await Do_Not_Disturb_Channel.delete()
#     if Mute_Immune_Role is not None:
#         await Mute_Immune_Role.delete()

class HelpMenu(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="/setup", description="Gives More information about the setup command"),
            discord.SelectOption(label="/talk_with", description="Gets more information about the talk_with command"),
            discord.SelectOption(label="Do Not Disturb Channel", description="Gives more information about the Do Not Disturb channel"),
            discord.SelectOption(label="Mute Immune Role", description="Gives more information about the Mute Immune role"),
            
        ]
        super().__init__(placeholder="Choose an option...", min_values=1, max_values=1, options=options)



    async def callback(self, interaction: discord.Interaction):
        Do_Not_Disturb_Channel = discord.utils.get(interaction.guild.voice_channels, name="Do Not Disturb")
        Mute_Immune_Role = discord.utils.get(interaction.guild.roles, name="Mute Immune")
        if Mute_Immune_Role is None:
            Mute_Immune_Role = types.SimpleNamespace(mention="Mute Immune")
            Mute_Immune_Role.mention = "\"Mute Immune\""
        if Do_Not_Disturb_Channel is None:
            Do_Not_Disturb_Channel = types.SimpleNamespace(mention="Do Not Disturb")
            Do_Not_Disturb_Channel.mention = "\"Do Not Disturb\""
        if self.values[0] == "/setup":
            await interaction.response.send_message(f"The /setup command sets up the bot by creating a {Mute_Immune_Role.mention} role and a {Do_Not_Disturb_Channel.mention} voice channel.\nUsage: /setup Category", ephemeral=True)
        elif self.values[0] == "/talk_with":
            await interaction.response.send_message(f"The /talk_with command allows you to move a user from the {Do_Not_Disturb_Channel.mention} channel to your current voice channel. \nIf the users Status is Do Not Disturb, they will be notified, but they can still choose to join your channel. \nYou must be in a voice channel to use this command.", ephemeral=True)
        elif self.values[0] == "Do Not Disturb Channel":
            await interaction.response.send_message(f"The '{Do_Not_Disturb_Channel.mention}' channel is a voice channel where users can join to avoid being disturbed.\nUsers can't speak in this channel.\nYou can be moved to another channel by someone using the /talk_with command. To avoid being moved, consider setting your status to Do Not Disturb.", ephemeral=True)
        elif self.values[0] == "Mute Immune Role":
            await interaction.response.send_message(f"The '{Mute_Immune_Role.mention}' role is a role that allows users to speak in the '{Do_Not_Disturb_Channel.mention}' channel.\nThis role is typically assigned to Bots such as a music bot.", ephemeral=True)

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(HelpMenu())

@client.tree.command(name="help", description="Lists all bot features")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title="Help", description="Lists all bot features:", color=discord.Color.blue())
    embed.add_field(name="/setup", value="Sets up the bot.", inline=False)
    embed.add_field(name="/talk_with", value="Asks a user to talk with you.", inline=False)
    embed.add_field(name="Do Not Disturb Channel", value="A voice channel where users can join to avoid being disturbed.", inline=False)
    embed.add_field(name="Mute Immune Role", value="A role that allows users to speak in the 'Do Not Disturb' channel.", inline=False)
    embed.set_footer(text="Select an option from the dropdown menu for more information.")
    await interaction.response.send_message(embed=embed, view=HelpView(), ephemeral=True)

@client.tree.command(name="talk_with", description="Asks a user to talk with you, even if they are in Do Not Disturb mode.")
@app_commands.describe(user="The user you want to talk with.")
async def talk_with(interaction: discord.Interaction, user: discord.Member):
    if not interaction.user.voice:
        await interaction.response.send_message("You must be in a voice channel to talk with someone.", ephemeral=True)
        return

    Do_Not_Disturb_Channel = discord.utils.get(interaction.guild.voice_channels, name="Do Not Disturb")
            
    if interaction.user.voice.channel == Do_Not_Disturb_Channel:
        await interaction.response.send_message("You cannot talk with someone while in the Do Not Disturb channel.", ephemeral=True)
        return

    
    user = interaction.guild.get_member(user.id)

    if user.status == discord.Status.dnd:
        invite = await interaction.user.voice.channel.create_invite(unique=False )
        await user.send(f"User {interaction.user.display_name} wants to talk with you in {interaction.user.voice.channel.name}. \n{invite.url}")
        await interaction.response.send_message(f"{user.mention} is in Do Not Disturb mode but has been sent a DM that you want to talk with them.", ephemeral=True)
        return

    if not user.voice:
        await interaction.response.send_message(f"{user.mention} is not in a voice channel.", ephemeral=True)
        return
    if user.voice.channel == Do_Not_Disturb_Channel:
        await user.move_to(interaction.user.voice.channel)
        await interaction.response.send_message(f"{user.mention} has been moved to your voice channel.", ephemeral=True)
    else:
        await interaction.response.send_message(f"{user.mention} is not in the Do Not Disturb channel.", ephemeral=True)
    
@client.tree.command(name="source", description="Provides the source code of the bot.")
async def source_code(interaction: discord.Interaction):
    await interaction.response.send_message("You can find the source code of this bot on GitHub: [Source Code](https://github.com/Gladiatorsarius/Discord_No_Disturb_Bot)", ephemeral=True)


client.run(discord_token,log_handler=handler, log_level=logging.DEBUG)