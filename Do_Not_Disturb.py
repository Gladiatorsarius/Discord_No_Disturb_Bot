import discord
import os
from dotenv import load_dotenv
from discord.ext import commands, tasks
import logging
from discord import app_commands
from types import SimpleNamespace
import git_commands
import subprocess

#region Variables
__Version__ = "1.3.1"

In_Testing = os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "testing.txt"))

load_dotenv()
if In_Testing:
    discord_token = os.getenv('Discord_Token_Testing')
else: 
    discord_token = os.getenv('Discord_Token')

Dev_Guild_ID = discord.Object(id=(os.getenv('Dev_Guild_ID')))
Developer_ID = discord.Object(id=(os.getenv('Developer_ID')))

Original_Source_Code_URL = "https://github.com/Gladiatorsarius/Discord_No_Disturb_Bot" #Please do not change this URL. It is used to provide credit to the original author of the bot.
Original_Author_ID = discord.Object(id=1130514544960225402) #Please do not change this id. It is used to provide credit to the original author of the bot.
Original_Author_Name = "Gladiatorsarius" #Please do not change this name. It is used to provide credit to the original author of the bot.

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
#endregion
#region Bot Setup
class Client(commands.Bot):
    async def setup_hook(self):
        try:
            if not In_Testing:
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
        await self.get_user(Developer_ID.id).send(f"Bot Started Sucesfully. Version: {__Version__}")
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
client = Client(intents=intents ,command_prefix='!')
#endregion

#region Helper Functions
def check_developer_id(user_id: int) -> bool:
    return user_id == Developer_ID.id

def is_developer():
    async def predicate(interaction: discord.Interaction):
        return check_developer_id(interaction.user.id)
    return app_commands.check(predicate)

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
@client.tree.command(name="setup" , description="Sets up the Bot" )
@app_commands.checks.has_permissions(administrator=True)
@app_commands.describe(category="The category under which the 'Do Not Disturb' channel will be created. If not specified, it will be created as an uncategorized voice channel.", 
                       default_role="The role that will be given permission to mute in the 'Do Not Disturb' channel. If not specified, @everyone will be used.")
async def setup(interaction: discord.Interaction, category: discord.CategoryChannel = None, default_role: discord.Role = None):
    setup_progress = "Setting up the bot..."
    do_not_disturb_channel_message = "Waiting for previous steps to complete..."
    do_not_disturb_permission_everyone_message = "Waiting for previous steps to complete..."
    do_not_disturb_permission_mute_immune_message = "Waiting for previous steps to complete..."
    mute_immune_role_message = "Waiting for previous steps to complete..."
    locked_in_role_message = "Waiting for previous steps to complete..."


    async def update_embed(step_message):
        nonlocal setup_progress
        if step_message == 5:
            setup_progress = "Setup completed successfully!"
        embed = discord.Embed(title="Setup Progress", description=setup_progress, color=discord.Color.blue())
        embed.add_field(name="Mute Immune Role", value=f"{mute_immune_role_message}", inline=False)
        embed.add_field(name="Do Not Disturb Channel", value=f"{do_not_disturb_channel_message}", inline=False)
        embed.add_field(name="Do Not Disturb Permissions", value=f"{do_not_disturb_permission_everyone_message}", inline=False)
        embed.add_field(name="Mute Immune Permissions", value=f"{do_not_disturb_permission_mute_immune_message}", inline=False)
        embed.add_field(name="Locked In Role", value=f"{locked_in_role_message}", inline=False)
        embed.set_footer(text=f"{step_message}/5 Steps completed.")
        return embed

    await interaction.response.send_message(embed=await update_embed(0), ephemeral=True)


    mute_immune_role_message = "Checking 'Mute Immune' role..."
    await interaction.edit_original_response(embed=await update_embed(0))
    
    Mute_Immune_Role = get_Mute_Immune_Role(interaction.guild)
    if Mute_Immune_Role is None:
        await interaction.guild.create_role(name="Mute Immune")
        Mute_Immune_Role = get_Mute_Immune_Role(interaction.guild)
        mute_immune_role_message = f"Created {Mute_Immune_Role.mention} role. :white_check_mark: "
    else:
        mute_immune_role_message = f"{Mute_Immune_Role.mention} role exists. :white_check_mark: "


    do_not_disturb_channel_message = "Checking if 'Do Not Disturb channel' exists :arrows_clockwise: ... "
    await interaction.edit_original_response(embed=await update_embed(1))

    Do_Not_Disturb_Channel = get_Do_Not_Disturb_Channel(interaction.guild)
    if default_role is None:
        default_role = interaction.guild.default_role
    if Do_Not_Disturb_Channel is None:
        await interaction.guild.create_voice_channel(name ="Do Not Disturb" , category=category)
        Do_Not_Disturb_Channel = get_Do_Not_Disturb_Channel(interaction.guild)
        do_not_disturb_channel_message = f"Created {Do_Not_Disturb_Channel.mention} channel. {"As Uncategorized Voice Channel" if category is None else f"Under {category.name}"} :white_check_mark: "

        do_not_disturb_permission_everyone_message = f"Setting 'Do Not Disturb' channel permissions for {default_role.mention} :arrows_clockwise: ..."
        await interaction.edit_original_response(embed=await update_embed(2))

        await Do_Not_Disturb_Channel.set_permissions(default_role, connect=True, speak=False)
        do_not_disturb_permission_everyone_message = f"Set 'Do Not Disturb' channel permissions for {default_role.mention} to not speak. :white_check_mark: "

        do_not_disturb_permission_mute_immune_message = f"Setting 'Do Not Disturb' channel permissions for {Mute_Immune_Role.mention} :arrows_clockwise: ..."
        await interaction.edit_original_response(embed=await update_embed(3))

        await Do_Not_Disturb_Channel.set_permissions(Mute_Immune_Role, speak=True)
        do_not_disturb_permission_mute_immune_message = f"Set 'Do Not Disturb' channel permissions for {Mute_Immune_Role.mention} to speak. :white_check_mark: "

    else:
        do_not_disturb_channel_message = f"{Do_Not_Disturb_Channel.mention} channel exists. :white_check_mark: "
        do_not_disturb_permission_everyone_message = f"Checking  'Do Not Disturb' channel permissions for {default_role.mention} :arrows_clockwise: ..."
        await interaction.edit_original_response(embed=await update_embed(2))
        if Do_Not_Disturb_Channel.permissions_for(default_role).speak is not False:
            await Do_Not_Disturb_Channel.set_permissions(default_role, connect=True, speak=False)
            do_not_disturb_permission_everyone_message = f"Set 'Do Not Disturb' channel permissions for {default_role.mention} to not speak. :white_check_mark: "
        else:
            do_not_disturb_permission_everyone_message = f"'Do Not Disturb' channel permissions for {default_role.mention} are already set to not speak. :white_check_mark: "

        do_not_disturb_permission_mute_immune_message = f"Checking 'Do Not Disturb' channel permissions for {Mute_Immune_Role.mention} :arrows_clockwise: ..."
        await interaction.edit_original_response(embed=await update_embed(3))
        if Do_Not_Disturb_Channel.permissions_for(Mute_Immune_Role).speak is not True:
            await Do_Not_Disturb_Channel.set_permissions(Mute_Immune_Role, speak=True)
            do_not_disturb_permission_mute_immune_message = f"Set 'Do Not Disturb' channel permissions for {Mute_Immune_Role.mention} to speak. :white_check_mark: "
        else:
            do_not_disturb_permission_mute_immune_message = f"'Do Not Disturb' channel permissions for {Mute_Immune_Role.mention} are already set to speak. :white_check_mark: "
        

    locked_in_role_message = "Checking 'Locked In' role... :arrows_clockwise:"
    await interaction.edit_original_response(embed=await update_embed(4))
    Locked_In_Role = get_Locked_In_Role(interaction.guild)
    if Locked_In_Role is None:
        await interaction.guild.create_role(name="Locked In")
        Locked_In_Role = get_Locked_In_Role(interaction.guild)
        locked_in_role_message = f"Created {Locked_In_Role.mention} role. :white_check_mark: "
    else:
        locked_in_role_message = f"{Locked_In_Role.mention} role exists. :white_check_mark: "
    await interaction.edit_original_response(embed=await update_embed(5))


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


#region Unrelated features and commands(Not Neaded for the bot to work)
#region Git Related Commands
#region Version Command       
class pull_change_confirmationView(discord.ui.View):
    @discord.ui.button(label="⚠️ Confirm", style=discord.ButtonStyle.danger)
    async def pull_changes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not check_developer_id(interaction.user.id):
            await interaction.response.send_message("You do not have permission to pull changes.", ephemeral=True)
            return
        pulled = git_commands.git_pull()
        embed = discord.Embed(title="Changes Pulled", description=pulled, color=discord.Color.green())
        embed.add_field(name="Restarting Bot", value="The bot will now restart to apply the changes.", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        subprocess.run(["systemctl" , "restart", "Do_Not_Disturb_Bot"])

class pull_changeView(discord.ui.View):
    @discord.ui.button(label="Pull Changes", style=discord.ButtonStyle.danger)
    async def pull_changes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not check_developer_id(interaction.user.id):
            await interaction.response.send_message("You do not have permission to pull changes.", ephemeral=True)
            return
        behind_Main = git_commands.git_differences("commit_count")
        embed = discord.Embed(title="Pull Changes", description=f"Please confirm pulling {behind_Main} {'commit' if behind_Main == 1 else 'commits'} from Github and Restarting the bot", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, view=pull_change_confirmationView(), ephemeral=True)
    

class show_file_differencesView(pull_changeView):
    @discord.ui.button(label="See changed files", style=discord.ButtonStyle.primary)
    async def see_file_differences(self, interaction: discord.Interaction, button: discord.ui.Button):
        differences = git_commands.git_diff("stat")  
        embed = discord.Embed(title="Changed Files", description=differences, color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, view=pull_changeView(), ephemeral=True)


class show_commitsView(discord.ui.View):
    @discord.ui.button(label="Show commits", style=discord.ButtonStyle.primary)
    async def show_commit_links(self, interaction: discord.Interaction, button: discord.ui.Button):
        commit_links = git_commands.commit_links()
        short_hashes_with_commit_messages = git_commands.git_differences("short_hash_with_commit_message")

        commit_messages_with_links = []
        for i in range(len(commit_links)):
            commit_messages_with_links.append(f"[{short_hashes_with_commit_messages[i]}]({commit_links[i]})")

        embed = discord.Embed(title="Commits", description="Unmerged changes", color=discord.Color.blue())
        for i in range(len(commit_messages_with_links)):
            embed.add_field(name="", value=commit_messages_with_links[i], inline=False)
        await interaction.response.send_message(embed=embed, view=show_file_differencesView(), ephemeral=True)


@client.tree.command(name="version", description="Shows the current version of the bot.")
async def version(interaction: discord.Interaction):
    behind_Main = git_commands.git_differences("commit_count")
    if behind_Main != "0":
        embed = discord.Embed(title=f"Current Version: {__Version__}", description=f"The current version is not up to date with the latest version on [GitHub]({git_commands.git_url_origin()}).", color=discord.Color.red())
        embed.add_field(name="GitHub Version", value=f"{git_commands.get_remote_version()}", inline=False)
        embed.add_field(name="Behind Commits", value=f"The Bot is {behind_Main} commits behind.", inline=False)
        await interaction.response.send_message(embed=embed, view=show_commitsView(), ephemeral=True)
    else:
        embed = discord.Embed(title=f"Current Version: {__Version__}", description=f"The current version is up to date with the latest version on [GitHub]({git_commands.git_url_origin()}).", color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)
#endregion  

#region Source Code Command
@client.tree.command(name="source", description="Provides the source code of the bot.")
async def source_code(interaction: discord.Interaction):
    git_url_origin = git_commands.git_url_origin()
    Original_Author = interaction.guild.get_member(Original_Author_ID.id)
    if Original_Author is None:
        Original_Author = SimpleNamespace(mention=Original_Author_Name)
    if git_url_origin is None or git_url_origin == Original_Source_Code_URL:
        await interaction.response.send_message(f"This Bot is Developed by {Original_Author.mention}\nYou can find the source code of this bot on GitHub: [Source Code]({Original_Source_Code_URL})", ephemeral=True)
    else:
        author = git_commands.author_name()
        await interaction.response.send_message(f"This Bot Version of the Bot got modified by {author}\nYou can find the source code of this bot on GitHub: [Source Code]({git_url_origin}) \nThis Bot was originally developed by {Original_Author.mention} \nYou can find the original source code on GitHub: [Original Source Code]({Original_Source_Code_URL})", ephemeral=True)
#endregion
#endregion

#region Testing Commands and Status Task
if In_Testing:
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

    @client.tree.command(name="undo_setup", description="Undoes the setup of the bot")
    @app_commands.checks.has_permissions(administrator=True)
    async def undo_setup(interaction: discord.Interaction):
        await interaction.response.send_message("Undoing setup...", ephemeral=True)
        Do_Not_Disturb_Channel = get_Do_Not_Disturb_Channel(interaction.guild)
        Mute_Immune_Role = get_Mute_Immune_Role(interaction.guild)
        Locked_In_Role = get_Locked_In_Role(interaction.guild)
        if Do_Not_Disturb_Channel is not None:
            await Do_Not_Disturb_Channel.delete()
        if Mute_Immune_Role is not None:
            await Mute_Immune_Role.delete()
        if Locked_In_Role is not None:
            await Locked_In_Role.delete()

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
else:
    @tasks.loop(minutes=30)
    async def status_task():
        behind_Main = git_commands.git_differences("commit_count")

        if behind_Main != "0":
            Developer = client.get_user(Developer_ID.id)
            dm_channel = Developer.dm_channel or await Developer.create_dm()
            last_message = None
            async for msg in dm_channel.history(limit=50):
                if msg.author == client.user:
                    last_message = msg
                    break
            embed = discord.Embed(title=f"Current Version: {__Version__}", description=f"The current version is not up to date with the latest version on [GitHub]({git_commands.git_url_origin()}).", color=discord.Color.red())
            embed.add_field(name="GitHub Version", value=f"{git_commands.get_remote_version()}", inline=False)
            embed.add_field(name="Behind Commits", value=f"The Bot is {behind_Main} commits behind.", inline=False)
            if not last_message or not last_message.embeds == embed:
                await Developer.send(embed=embed, view=show_commitsView())


@status_task.before_loop
async def before_status_task():
    await client.wait_until_ready()
#endregion
#endregion

client.run(discord_token,log_handler=handler, log_level=logging.DEBUG)

