import os

import discord
from discord.ext import commands
import asyncio
from help_cog import help_cog
from music_cog import music_cog
from dotenv import load_dotenv
from search_cog import search_cog

load_dotenv()
TOKEN_DISCORD=os.getenv("TOKEN_DISCORD")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

#remove the default help command so that we can write out own
bot.remove_command('help')

@bot.event
async def on_ready():
    print("BOT iniciado com sucesso!")

async def main():
    async with bot:
        await bot.add_cog(help_cog(bot))
        await bot.add_cog(music_cog(bot))
        await bot.add_cog(search_cog(bot))
        await bot.start(TOKEN_DISCORD)

asyncio.run(main())

# bot.run(TOKEN_DISCORD)