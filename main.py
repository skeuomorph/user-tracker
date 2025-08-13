import discord
from discord.ext import commands
import json
import os

# Set up intents for the bot
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

# Initialize bot with command prefix
bot = commands.Bot(command_prefix="!", intents=intents)

# File to store monitored users data
MONITORED_FILE = "monitored_users.json"

# Initialize monitored users file if it doesn't exist
if not os.path.exists(MONITORED_FILE):
    with open(MONITORED_FILE, "w") as f:
        json.dump({}, f)

def load_monitored():
    """Load monitored users data from JSON file"""
    try:
        with open(MONITORED_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return empty dict if file doesn't exist or is corrupted
        return {}

def save_monitored(data):
    """Save monitored users data to JSON file"""
    try:
        with open(MONITORED_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving monitored users data: {e}")

@bot.event
async def on_ready():
    """Event triggered when bot is ready and connected"""
    print(f"Logged in as {bot.user}")
    if bot.user:
        print(f"Bot ID: {bot.user.id}")
    print("Discord Bot is ready and running!")
    
    # Set bot status - you can customize this message
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.playing, 
        name="Moderation Assistant"
    ))

@bot.command()
@commands.has_permissions(manage_messages=True)
async def monitor(ctx, user: discord.User):
    """Command to start monitoring a user's messages"""
    try:
        data = load_monitored()
        guild_id = str(ctx.guild.id)
        
        # Initialize guild data if not exists
        if guild_id not in data:
            data[guild_id] = []
        
        # Add user to monitored list if not already monitored
        if str(user.id) not in data[guild_id]:
            data[guild_id].append(str(user.id))
            save_monitored(data)
            
            # Create embed for success message
            embed = discord.Embed(
                title="✅ User Monitoring Started",
                description=f"{user.mention} is now being monitored.",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
            embed.add_field(name="User ID", value=user.id, inline=True)
            embed.add_field(name="Added by", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
        else:
            # User already monitored
            embed = discord.Embed(
                title="⚠️ Already Monitored",
                description=f"{user.mention} is already being monitored.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description=f"Failed to monitor user: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def monitor_id(ctx, user_id: str):
    """Command to start monitoring a user by their Discord ID"""
    try:
        # Validate that the input is a valid Discord ID (snowflake)
        try:
            user_id_int = int(user_id)
            if user_id_int <= 0 or len(user_id) < 17 or len(user_id) > 20:
                raise ValueError("Invalid Discord ID format")
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid User ID",
                description="Please provide a valid Discord user ID (17-20 digit number).",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        data = load_monitored()
        guild_id = str(ctx.guild.id)
        
        # Initialize guild data if not exists
        if guild_id not in data:
            data[guild_id] = []
        
        # Add user to monitored list if not already monitored
        if user_id not in data[guild_id]:
            data[guild_id].append(user_id)
            save_monitored(data)
            
            # Try to fetch user information for the embed
            try:
                user = await bot.fetch_user(user_id_int)
                user_display = f"{user.name}#{user.discriminator}" if user.discriminator != "0" else user.name
                user_mention = user.mention
                user_avatar = user.avatar.url if user.avatar else user.default_avatar.url
            except:
                # User not found or can't be fetched
                user_display = f"User ID: {user_id}"
                user_mention = f"<@{user_id}>"
                user_avatar = None
            
            # Create embed for success message
            embed = discord.Embed(
                title="✅ User Monitoring Started (by ID)",
                description=f"{user_mention} is now being monitored.",
                color=discord.Color.green()
            )
            if user_avatar:
                embed.set_thumbnail(url=user_avatar)
            embed.add_field(name="User ID", value=user_id, inline=True)
            embed.add_field(name="User", value=user_display, inline=True)
            embed.add_field(name="Added by", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
        else:
            # User already monitored
            embed = discord.Embed(
                title="⚠️ Already Monitored",
                description=f"User ID `{user_id}` is already being monitored.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description=f"Failed to monitor user by ID: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def unmonitor(ctx, user: discord.User):
    """Command to stop monitoring a user's messages"""
    try:
        data = load_monitored()
        guild_id = str(ctx.guild.id)
        
        # Check if user is monitored and remove them
        if guild_id in data and str(user.id) in data[guild_id]:
            data[guild_id].remove(str(user.id))
            save_monitored(data)
            
            # Create embed for success message
            embed = discord.Embed(
                title="✅ User Monitoring Stopped",
                description=f"{user.mention} is no longer being monitored.",
                color=discord.Color.green()
            )
            embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
            embed.add_field(name="User ID", value=user.id, inline=True)
            embed.add_field(name="Removed by", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
        else:
            # User was not monitored
            embed = discord.Embed(
                title="⚠️ Not Monitored",
                description=f"{user.mention} was not being monitored.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description=f"Failed to unmonitor user: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def unmonitor_id(ctx, user_id: str):
    """Command to stop monitoring a user by their Discord ID"""
    try:
        # Validate that the input is a valid Discord ID
        try:
            user_id_int = int(user_id)
            if user_id_int <= 0 or len(user_id) < 17 or len(user_id) > 20:
                raise ValueError("Invalid Discord ID format")
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid User ID",
                description="Please provide a valid Discord user ID (17-20 digit number).",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        data = load_monitored()
        guild_id = str(ctx.guild.id)
        
        # Check if user is monitored and remove them
        if guild_id in data and user_id in data[guild_id]:
            data[guild_id].remove(user_id)
            save_monitored(data)
            
            # Try to fetch user information for the embed
            try:
                user = await bot.fetch_user(user_id_int)
                user_display = f"{user.name}#{user.discriminator}" if user.discriminator != "0" else user.name
                user_mention = user.mention
                user_avatar = user.avatar.url if user.avatar else user.default_avatar.url
            except:
                # User not found or can't be fetched
                user_display = f"User ID: {user_id}"
                user_mention = f"<@{user_id}>"
                user_avatar = None
            
            # Create embed for success message
            embed = discord.Embed(
                title="✅ User Monitoring Stopped (by ID)",
                description=f"{user_mention} is no longer being monitored.",
                color=discord.Color.green()
            )
            if user_avatar:
                embed.set_thumbnail(url=user_avatar)
            embed.add_field(name="User ID", value=user_id, inline=True)
            embed.add_field(name="User", value=user_display, inline=True)
            embed.add_field(name="Removed by", value=ctx.author.mention, inline=True)
            
            await ctx.send(embed=embed)
        else:
            # User was not monitored
            embed = discord.Embed(
                title="⚠️ Not Monitored",
                description=f"User ID `{user_id}` was not being monitored.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description=f"Failed to unmonitor user by ID: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def monitored(ctx):
    """Command to list all monitored users in the guild"""
    try:
        data = load_monitored()
        guild_id = str(ctx.guild.id)
        
        if guild_id not in data or not data[guild_id]:
            embed = discord.Embed(
                title="📋 Monitored Users",
                description="No users are currently being monitored in this server.",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
            return
        
        # Get user objects for monitored user IDs
        monitored_users = []
        for user_id in data[guild_id]:
            try:
                user = await bot.fetch_user(int(user_id))
                monitored_users.append(f"{user.mention} (`{user.id}`)")
            except:
                # User not found, remove from list
                monitored_users.append(f"Unknown User (`{user_id}`)")
        
        embed = discord.Embed(
            title="📋 Monitored Users",
            description="\n".join(monitored_users),
            color=discord.Color.blue()
        )
        embed.add_field(name="Total Count", value=len(monitored_users), inline=True)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Error",
            description=f"Failed to list monitored users: {str(e)}",
            color=discord.Color.red()
        )
        await ctx.send(embed=error_embed)

@bot.command(name='commands')
@commands.has_permissions(manage_messages=True)
async def commands_help(ctx):
    """Command to show available bot commands"""
    embed = discord.Embed(
        title="📚 Discord Moderation Bot Commands",
        description="Commands for monitoring users and managing the watchlist",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="👁️ Monitor by Mention", 
        value="`!monitor @user` - Start monitoring a user by mentioning them",
        inline=False
    )
    
    embed.add_field(
        name="🆔 Monitor by ID", 
        value="`!monitor_id <user_id>` - Start monitoring a user by their Discord ID",
        inline=False
    )
    
    embed.add_field(
        name="👁️‍🗨️ Unmonitor by Mention", 
        value="`!unmonitor @user` - Stop monitoring a user by mentioning them",
        inline=False
    )
    
    embed.add_field(
        name="🆔 Unmonitor by ID", 
        value="`!unmonitor_id <user_id>` - Stop monitoring a user by their Discord ID",
        inline=False
    )
    
    embed.add_field(
        name="📋 View Watchlist", 
        value="`!monitored` - Show all currently monitored users",
        inline=False
    )
    
    embed.add_field(
        name="❓ Commands", 
        value="`!commands` - Show this help message",
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ How to get a User ID",
        value="Enable Developer Mode in Discord settings, then right-click any user and select 'Copy User ID'",
        inline=False
    )
    
    embed.set_footer(text="All commands require 'Manage Messages' permission to use")
    
    await ctx.send(embed=embed)

@bot.event
async def on_message(message):
    """Event triggered when a message is sent"""
    # Ignore bot messages
    if message.author.bot:
        return
    
    # Skip if message is not from a guild
    if not message.guild:
        return
    
    try:
        data = load_monitored()
        guild_id = str(message.guild.id)
        
        # Check if user is monitored
        if guild_id in data and str(message.author.id) in data[guild_id]:
            # Find or create the tracked-users channel
            mod_log_channel = discord.utils.get(message.guild.text_channels, name="tracked-users")
            
            if not mod_log_channel:
                # Try to create the channel if it doesn't exist
                try:
                    mod_log_channel = await message.guild.create_text_channel(
                        name="tracked-users",
                        topic="Logs for monitored user messages",
                        reason="Auto-created by user tracking bot"
                    )
                except discord.Forbidden:
                    print(f"Missing permissions to create tracked-users channel in {message.guild.name}")
                    return
            
            if mod_log_channel:
                # Create embed for the logged message
                embed = discord.Embed(
                    title="📝 Monitored Message",
                    description=message.content or "*No text content*",
                    color=discord.Color.red()
                )
                
                # Set author information
                embed.set_author(
                    name=f"{message.author} ({message.author.id})", 
                    icon_url=message.author.avatar.url if message.author.avatar else message.author.default_avatar.url
                )
                
                # Add channel and timestamp information
                embed.add_field(name="Channel", value=message.channel.mention, inline=True)
                embed.add_field(name="Message ID", value=message.id, inline=True)
                embed.timestamp = message.created_at
                
                # Add attachment information if present
                if message.attachments:
                    attachment_info = []
                    for attachment in message.attachments:
                        attachment_info.append(f"[{attachment.filename}]({attachment.url})")
                    embed.add_field(name="Attachments", value="\n".join(attachment_info), inline=False)
                
                # Add jump link to original message
                embed.add_field(name="Jump to Message", value=f"[Click here]({message.jump_url})", inline=True)
                
                await mod_log_channel.send(embed=embed)
                
    except Exception as e:
        print(f"Error logging monitored message: {e}")
    
    # Process commands
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ Missing Permissions",
            description="You need the `Manage Messages` permission to use this command.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.UserNotFound):
        embed = discord.Embed(
            title="❌ User Not Found",
            description="Could not find the specified user. Please check the username or ID.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="❌ Missing Argument",
            description=f"Please provide a user to {ctx.command.name}.\nUsage: `!{ctx.command.name} @user`",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    else:
        # Log unexpected errors
        print(f"Unexpected error in command {ctx.command}: {error}")
        embed = discord.Embed(
            title="❌ Unexpected Error",
            description="An unexpected error occurred. Please try again later.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

# Start the bot
if __name__ == "__main__":
    # Get Discord token from environment variables
    token = os.getenv("DISCORD_TOKEN")
    
    if not token:
        print("ERROR: DISCORD_TOKEN environment variable not found!")
        print("Please set your Discord bot token in the Replit secrets.")
        exit(1)
    
    try:
        # Run the bot
        bot.run(token)
    except discord.LoginFailure:
        print("ERROR: Invalid Discord token provided!")
    except Exception as e:
        print(f"ERROR: Failed to start bot: {e}")