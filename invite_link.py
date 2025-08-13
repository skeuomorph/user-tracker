import os

# Bot ID from the console logs
BOT_ID = "1400491086840860855"

# Required permissions for the Discord bot
# Read Messages/View Channels, Send Messages, Manage Messages, Embed Links, 
# Read Message History, Manage Channels
PERMISSIONS = 268445760

# Generate the invite link
invite_url = f"https://discord.com/api/oauth2/authorize?client_id={BOT_ID}&permissions={PERMISSIONS}&scope=bot"

print("Discord Bot Invite Link:")
print("=" * 50)
print(invite_url)
print("=" * 50)
print("\nPermissions included:")
print("- Read Messages/View Channels")
print("- Send Messages") 
print("- Manage Messages")
print("- Embed Links")
print("- Read Message History")
print("- Manage Channels (for creating #tracked-users channel)")
print("\nClick the link above to invite your bot to a Discord server!")