import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # Habilitar Message Content Intent
bot = commands.Bot(command_prefix='!', intents=intents)  # Definindo a instância do bot corretamente
