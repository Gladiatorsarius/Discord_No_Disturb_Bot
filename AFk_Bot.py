import discord
import os
from dotenv import load_dotenv
from discord.ext import commands, tasks
import logging
from discord import app_commands


load_dotenv()
discord_token = os.getenv('AFK_Voice_Token')

Do_Not_Disturb_Channel = 1538970413315530752

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')



class Client(commands.Bot):
    async def setup_hook(self):
        guild = discord.Object(id=1537433277445574676)
        try:
            self.tree.copy_global_to(guild=guild)
            synced_guild = await self.tree.sync(guild=guild)
            print(f"Synced {len(synced_guild)} commands to the guild {guild.id}.")

            self.tree.clear_commands(guild=None)
            await self.tree.sync()
            print("Cleared global commands.")
        except Exception as e:
            print(f"Error syncing commands: {e}")

    async def on_ready(self):
        print(f'Logged in as {self.user.name}')
        if not status_task.is_running():
            status_task.start()

intents = discord.Intents.all()
client = Client(intents=intents ,command_prefix='!')


@client.tree.command(name="restart", description="Restarts the bot")
async def restart(interaction: discord.Interaction):
    await interaction.response.send_message("Restarting the bot...")
    print("/restart command received.Shutting down...")
    with open("startup.txt", "w") as f:
        pass
    await interaction.client.close()

@client.tree.command(name="shutdown", description="Shuts down the bot")
async def shutdown(interaction: discord.Interaction):
    await interaction.response.send_message("Shutting down the bot...")
    print("/shutdown command received. Shutting down...")
    await client.close()

@tasks.loop(seconds=1)
async def status_task():
    if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "shutdown.txt")):
        print("Shutdown signal received. Shutting down...")
        os.remove(os.path.join(os.path.dirname(os.path.abspath(__file__)), "shutdown.txt"))
        with open("startup.txt", "w") as f:
            pass
        await client.close()

@status_task.before_loop
async def before_status_task():
    await client.wait_until_ready()

@client.event
async def on_voice_state_update(member, before, after):
    if after.channel.id == Do_Not_Disturb_Channel:
        if member.guild_permissions.administrator:
            await member.edit(mute=True)
        
    elif after.channel.id != Do_Not_Disturb_Channel:
        if member.guild_permissions.administrator:
            await member.edit(mute=False)

@client.tree.command(name="do_not_disturb" , description="Sets yourself to do not disturb")
async def do_not_disturb(interaction: discord.Interaction):

    if interaction.user.voice and interaction.user.voice.channel.id != Do_Not_Disturb_Channel:
        await interaction.user.move_to(discord.Object(id=Do_Not_Disturb_Channel))
        await interaction.response.send_message("You have been moved to the Do Not Disturb channel.", ephemeral=True)
    else:
        await interaction.response.send_message("You are already in the Do Not Disturb channel or not in a voice channel.", ephemeral=True)


@client.tree.command(name="talk_with", description="Moves a user into your voice if they are in the Do Not Disturb channel.")
@app_commands.describe(user="The user you want to move from AFK to your voice channel.")
async def talk_with(interaction: discord.Interaction, user: discord.Member):
    if interaction.user.voice and interaction.user.voice.channel.id != Do_Not_Disturb_Channel:
        user = interaction.guild.get_member(user.id)
        print(f"User {user.display_name} status: {user.status}")
        if user.status == discord.Status.dnd:
            invite = await interaction.user.voice.channel.create_invite(unique=False )
            await user.send(f"User {interaction.user.display_name} wants to talk with you in {interaction.user.voice.channel.name}. \nClick the link to join: {invite.url}")
            await interaction.response.send_message(f"Send {user.mention} a DM that you want to talk with them.", ephemeral=True)
            return

        if user.voice and user.voice.channel.id == Do_Not_Disturb_Channel:
            await user.move_to(interaction.user.voice.channel)
            await interaction.response.send_message(f"{user.mention} has been moved to your voice channel.", ephemeral=True)
        else:
            await interaction.response.send_message(f"{user.mention} is not in the Do Not Disturb channel.", ephemeral=True)
    else:
        await interaction.response.send_message("You must be in a voice channel to talk with someone.", ephemeral=True)
    



client.run(discord_token,log_handler=handler, log_level=logging.DEBUG)