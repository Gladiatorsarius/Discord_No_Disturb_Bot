import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import logging
from discord import app_commands
from types import SimpleNamespace
import asyncio
import basicdiscordbot

#region Variables
load_dotenv()



Dev_Guild_ID = int(os.getenv('Dev_Guild_ID'))
Changelog_Channel_ID = int(os.getenv("Changelog_Channel_ID"))

testing = os.getenv("testing").lower() == 'true'

Original_Source_Code_URL = "https://github.com/Gladiatorsarius/Discord_No_Disturb_Bot" #Please do not change this URL. It is used to provide credit to the original author of the bot.


if testing:
    discord_token = os.getenv('Discord_Token_Testing')
else: 
    discord_token = os.getenv('Discord_Token')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
#endregion

#region Bot Setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
client = commands.Bot(command_prefix="!", intents=intents)

@client.event
async def setup_hook():
    await client.add_cog(basicdiscordbot.BasicDiscordBot(client=client,
                                                   dev_guild_id=Dev_Guild_ID,
                                                   changelog_channel_id=Changelog_Channel_ID,
                                                   original_source_code_url=Original_Source_Code_URL,
                                                   testing=testing,
                                                   auto_pull=True,
                                                   auto_restart=True,
                                                   systemctl_name="Do_Not_Disturb_Bot"))
#endregion

#region Helper Functions

def get_Mute_Immune_Role(guild):
    return discord.utils.get(guild.roles, name="Mute Immune")

def get_Do_Not_Disturb_Channel(guild):
    return discord.utils.get(guild.voice_channels, name="Do Not Disturb")

def get_Locked_In_Role(guild):
    return discord.utils.get(guild.roles, name="Locked In")


#endregion

#region Bot Features and Commands

#region User Experience Commands
#region Setup Command
import asyncio
import discord
from discord import app_commands

@client.tree.command(name="setup", description="Sets up the Bot")
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(
    category="The category under which the 'Do Not Disturb' channel will be created. If not specified, it will be created as an uncategorized voice channel.",
    default_role="The role that will be given permission to mute in the 'Do Not Disturb' channel. If not specified, @everyone will be used."
)
async def setup(
    interaction: discord.Interaction, 
    category: discord.CategoryChannel = None, 
    default_role: discord.Role = None
):
    # Dictionary to keep track of individual step messages and completed count
    state = {
        "mute_immune": "Waiting for previous steps to complete...",
        "dnd_channel": "Waiting for previous steps to complete...",
        "perm_everyone": "Waiting for previous steps to complete...",
        "perm_mute_immune": "Waiting for previous steps to complete...",
        "locked_in": "Waiting for previous steps to complete...",
        "completed_steps": 0
    }

    async def update_embed():
        progress_title = "Setup completed successfully!" if state["completed_steps"] == 5 else "Setting up the bot..."
        
        embed = discord.Embed(title="Setup Progress", description=progress_title, color=discord.Color.blue())
        embed.add_field(name="Mute Immune Role", value=state["mute_immune"], inline=False)
        embed.add_field(name="Do Not Disturb Channel", value=state["dnd_channel"], inline=False)
        embed.add_field(name="Do Not Disturb Permissions", value=state["perm_everyone"], inline=False)
        embed.add_field(name="Mute Immune Permissions", value=state["perm_mute_immune"], inline=False)
        embed.add_field(name="Locked In Role", value=state["locked_in"], inline=False)
        embed.set_footer(text=f"{state['completed_steps']}/5 Steps completed.")
        
        await interaction.edit_original_response(embed=embed)

    # Send initial embed
    embed = discord.Embed(title="Setup Progress", description="Setting up the bot...", color=discord.Color.blue())
    embed.add_field(name="Mute Immune Role", value=state["mute_immune"], inline=False)
    embed.add_field(name="Do Not Disturb Channel", value=state["dnd_channel"], inline=False)
    embed.add_field(name="Do Not Disturb Permissions", value=state["perm_everyone"], inline=False)
    embed.add_field(name="Mute Immune Permissions", value=state["perm_mute_immune"], inline=False)
    embed.add_field(name="Locked In Role", value=state["locked_in"], inline=False)
    embed.set_footer(text="0/5 Steps completed.")
    await interaction.response.send_message(embed=embed, ephemeral=True)

    # Resolve default_role fallback
    if default_role is None:
        default_role = interaction.guild.default_role

    # ==================== STEP HELPER FUNCTIONS ====================

    async def task_mute_immune_role():
        state["mute_immune"] = "Checking 'Mute Immune' role..."
        await update_embed()
        
        mute_immune_role = get_Mute_Immune_Role(interaction.guild)
        if mute_immune_role is None:
            mute_immune_role = await interaction.guild.create_role(name="Mute Immune")
            state["mute_immune"] = f"Created {mute_immune_role.mention} role. :white_check_mark:"
        else:
            state["mute_immune"] = f"{mute_immune_role.mention} role exists. :white_check_mark:"
        
        state["completed_steps"] += 1
        await update_embed()
        return mute_immune_role

    async def task_locked_in_role():
        state["locked_in"] = "Checking 'Locked In' role... :arrows_clockwise:"
        await update_embed()
        
        locked_in_role = get_Locked_In_Role(interaction.guild)
        if locked_in_role is None:
            locked_in_role = await interaction.guild.create_role(name="Locked In")
            state["locked_in"] = f"Created {locked_in_role.mention} role. :white_check_mark:"
        else:
            state["locked_in"] = f"{locked_in_role.mention} role exists. :white_check_mark:"
        
        state["completed_steps"] += 1
        await update_embed()
        return locked_in_role

    async def task_dnd_channel():
        state["dnd_channel"] = "Checking if 'Do Not Disturb channel' exists :arrows_clockwise: ... "
        await update_embed()
        
        dnd_channel = get_Do_Not_Disturb_Channel(interaction.guild)
        if dnd_channel is None:
            dnd_channel = await interaction.guild.create_voice_channel(name="Do Not Disturb", category=category)
            category_text = "As Uncategorized Voice Channel" if category is None else f"Under {category.name}"
            state["dnd_channel"] = f"Created {dnd_channel.mention} channel. {category_text} :white_check_mark:"
        else:
            state["dnd_channel"] = f"{dnd_channel.mention} channel exists. :white_check_mark:"
        
        state["completed_steps"] += 1
        await update_embed()
        return dnd_channel

    async def task_everyone_permissions(dnd_channel):
        state["perm_everyone"] = f"Checking 'Do Not Disturb' channel permissions for {default_role.mention} :arrows_clockwise: ..."
        await update_embed()
        
        if dnd_channel.permissions_for(default_role).speak is not False:
            await dnd_channel.set_permissions(default_role, connect=True, speak=False)
            state["perm_everyone"] = f"Set 'Do Not Disturb' channel permissions for {default_role.mention} to not speak. :white_check_mark:"
        else:
            state["perm_everyone"] = f"'Do Not Disturb' channel permissions for {default_role.mention} are already set to not speak. :white_check_mark:"
        
        state["completed_steps"] += 1
        await update_embed()

    async def task_mute_immune_permissions(dnd_channel, mute_immune_role):
        state["perm_mute_immune"] = f"Checking 'Do Not Disturb' channel permissions for {mute_immune_role.mention} :arrows_clockwise: ..."
        await update_embed()
        
        if dnd_channel.permissions_for(mute_immune_role).speak is not True:
            await dnd_channel.set_permissions(mute_immune_role, speak=True)
            state["perm_mute_immune"] = f"Set 'Do Not Disturb' channel permissions for {mute_immune_role.mention} to speak. :white_check_mark:"
        else:
            state["perm_mute_immune"] = f"'Do Not Disturb' channel permissions for {mute_immune_role.mention} are already set to speak. :white_check_mark:"
        
        state["completed_steps"] += 1
        await update_embed()

    # ==================== CONCURRENT EXECUTION ====================

    # Phase 1: Create/check Mute Immune role, Locked In role, and DND channel in parallel
    mute_immune_role, _, dnd_channel = await asyncio.gather(
        task_mute_immune_role(),
        task_locked_in_role(),
        task_dnd_channel()
    )

    # Phase 2: Set permissions in parallel (dependent on Phase 1 results)
    await asyncio.gather(
        task_everyone_permissions(dnd_channel),
        task_mute_immune_permissions(dnd_channel, mute_immune_role)
    )


@setup.error
async def setup_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("You do not have permission to use this command.\nPls ask an administrator to set up the bot.", ephemeral=True)
#endregion

#region Help Command
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
        Do_Not_Disturb_Channel = get_Do_Not_Disturb_Channel(interaction.guild)
        Mute_Immune_Role = get_Mute_Immune_Role(interaction.guild)
        if Mute_Immune_Role is None:
            Mute_Immune_Role = SimpleNamespace(mention="Mute Immune")
            Mute_Immune_Role.mention = "Mute Immune"
        if Do_Not_Disturb_Channel is None:
            Do_Not_Disturb_Channel = SimpleNamespace(mention="Do Not Disturb")
            Do_Not_Disturb_Channel.mention = "Do Not Disturb"
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
#endregion

#region Undo Setup Command
if testing:
    @client.tree.command(name="undo_setup", description="Undoes the setup of the bot")
    @app_commands.checks.has_permissions(administrator=True)
    async def undo_setup(interaction: discord.Interaction):
        await interaction.response.send_message("Undoing setup...", ephemeral=True)
        Do_Not_Disturb_Channel = get_Do_Not_Disturb_Channel(interaction.guild)
        Mute_Immune_Role = get_Mute_Immune_Role(interaction.guild)
        Locked_In_Role = get_Locked_In_Role(interaction.guild)
        asyncio.gather(
            Do_Not_Disturb_Channel.delete() if Do_Not_Disturb_Channel else None,
            Mute_Immune_Role.delete() if Mute_Immune_Role else None,
            Locked_In_Role.delete() if Locked_In_Role else None
        )
#endregion
#endregion

#region Core Features
#region /Talk With Command
@client.tree.command(name="talk_with", description="Asks a user to talk with you, even if they are in Do Not Disturb mode.")
@app_commands.describe(user="The user you want to talk with.")
async def talk_with(interaction: discord.Interaction, user: discord.Member):
    if not interaction.user.voice:
        await interaction.response.send_message("You must be in a voice channel to talk with someone.", ephemeral=True)
        return

    Do_Not_Disturb_Channel = get_Do_Not_Disturb_Channel(interaction.guild)
            
    if interaction.user.voice.channel == Do_Not_Disturb_Channel:
        await interaction.response.send_message("You cannot talk with someone while in the Do Not Disturb channel.", ephemeral=True)
        return

    
    user = interaction.guild.get_member(user.id)

    if user.status == discord.Status.dnd or user.get_role(get_Locked_In_Role(interaction.guild).id):
        invite = await interaction.user.voice.channel.create_invite(unique=False )
        await user.send(f"{interaction.user.display_name} wants to talk with you in {interaction.user.voice.channel.name}. \n{invite.url}")
        await interaction.response.send_message(f"{user.mention} cant be moved directly, but has been sent a DM that you want to talk with them.", ephemeral=True)
        return

    if not user.voice:
        await interaction.response.send_message(f"{user.mention} is not in a voice channel.", ephemeral=True)
        return

    if user.voice.channel == Do_Not_Disturb_Channel:
        await interaction.response.send_message(f"{user.mention} will be moved to your voice channel, in 5 Seconds", ephemeral=True)
        await user.send(f"{interaction.user.display_name} wants to talk with you in {interaction.user.voice.channel.name}. You will be moved there in 5 seconds.")
        await asyncio.sleep(5) 
        await user.move_to(interaction.user.voice.channel)
        await interaction.followup.send(f"{user.mention} has been moved to your voice channel.", ephemeral=True)

    else:
        await interaction.response.send_message(f"{user.mention} is not in the Do Not Disturb channel.", ephemeral=True)
#endregion

#region Lock In Command
@client.tree.command(name="lock_in", description="Toggles the 'Locked In' which stops you from being moved out of the 'Do Not Disturb' channel.")
async def toggle_do_not_disturb(interaction: discord.Interaction):
    Locked_In_Role = get_Locked_In_Role(interaction.guild)
    if Locked_In_Role is None:
        await interaction.response.send_message("The 'Locked In' role does not exist. Please ask an administrator to run the /setup command.", ephemeral=True)
        return
    if interaction.user.get_role(Locked_In_Role.id):
        await interaction.user.remove_roles(Locked_In_Role)
        await interaction.response.send_message("Locked In Mode Toggled off", ephemeral=True)
    else:
        await interaction.user.add_roles(Locked_In_Role)
        await interaction.response.send_message("Locked In Mode Toggled on", ephemeral=True)
#endregion


@client.event
async def on_voice_state_update(member, before, after):
    if not member.guild_permissions.administrator:
        return
        
    Do_Not_Disturb_Channel = get_Do_Not_Disturb_Channel(after.channel.guild)

    Mute_Immune_Role = get_Mute_Immune_Role(after.channel.guild)
    if member.get_role(Mute_Immune_Role.id):
        return
    
    if after.channel == Do_Not_Disturb_Channel:
        await member.edit(mute=True)
    else:
        await member.edit(mute=False)
#endregion


#endregion

client.run(discord_token,log_handler=handler, log_level=logging.DEBUG)

