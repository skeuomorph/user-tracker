import json
import os
import discord
from discord.ext import commands

# Load the monitored users data
with open("monitored_users.json", "r") as f:
    data = json.load(f)

print("Discord Bot Watchlist Status")
print("=" * 40)

if not data:
    print("No users are currently being monitored.")
else:
    total_users = 0
    for guild_id, user_list in data.items():
        print(f"\nServer ID: {guild_id}")
        print(f"Monitored Users: {len(user_list)}")
        for user_id in user_list:
            print(f"  - User ID: {user_id}")
            total_users += 1
    
    print(f"\nTotal monitored users across all servers: {total_users}")
    print(f"Total servers with monitored users: {len(data)}")