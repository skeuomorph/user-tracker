import discord
from discord.ext import commands
import json
import os

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

MONITORED_FILE = "monitored_users.json"
if not os.path.exists(MONITORED_FILE):
    with open(MONITORED_FILE, "w") as f:
        json.dump({}, f)

def load_monitored():
    with open(MONITORED_FILE) as f:
        return json.load(f)

def save_monitored(data):
    with open(MONITORED_FILE, "w") as f:
        json.dump(data, f, indent=4)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def monitor(ctx, user: discord.User):
    data = load_monitored()
    guild_id = str(ctx.guild.id)

    if guild_id not in data:
        data[guild_id] = []

    if str(user.id) not in data[guild_id]:
        data[guild_id].append(str(user.id))
        save_monitored(data)
        await ctx.send(f"{user.mention} is now being monitored.")
    else:
        await ctx.send(f"{user.mention} is already monitored.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def unmonitor(ctx, user: discord.User):
    data = load_monitored()
    guild_id = str(ctx.guild.id)

    if guild_id in data and str(user.id) in data[guild_id]:
        data[guild_id].remove(str(user.id))
        save_monitored(data)
        await ctx.send(f"{user.mention} is no longer being monitored.")
    else:
        await ctx.send(f"{user.mention} was not monitored.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    data = load_monitored()
    guild_id = str(message.guild.id)
    if guild_id in data and str(message.author.id) in data[guild_id]:
        mod_log_channel = discord.utils.get(message.guild.text_channels, name="mod-log")
        if mod_log_channel:
            embed = discord.Embed(
                title="Monitored Message",
                description=message.content,
                color=discord.Color.red()
            )
            embed.set_author(name=f"{message.author} ({message.author.id})", icon_url=message.author.avatar.url if message.author.avatar else None)
            embed.add_field(name="Channel", value=message.channel.mention)
            embed.timestamp = message.created_at

            await mod_log_channel.send(embed=embed)

    await bot.process_commands(message)

# Start the bot
bot.run(os.environ["DISCORD_TOKEN"])