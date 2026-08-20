import discord
import os
from dotenv import load_dotenv
from discord.ext import commands, tasks
import logging

load_dotenv()
discord_token = os.getenv('AFK_Voice_Token')

AFK_Channel = 1538970413315530752
Summon_Channel = 1538985931934142596

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

intents = discord.Intents.default()
intents.message_content = True
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
    if after.channel.id == AFK_Channel:
        if member.guild_permissions.administrator:
            await member.edit(mute=True)
        
    elif before.channel.id == AFK_Channel:
        if member.guild_permissions.administrator:
            await member.edit(mute=False)
        
@client.tree.command(name="summon", description="Moves a user into your voice if they are in afk")
@client.tree.command.describe(user="The user you want to move from AFK to your voice channel.", voice="The voice channel you want to move the user to.")
async def summon(interaction: discord.Interaction, user: discord.Member, voice: discord.VoiceChannel):
    print(f"/summon command received. Moving {user} to {voice}.")



client.run(discord_token,log_handler=handler, log_level=logging.DEBUG)