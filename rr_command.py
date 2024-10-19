import discord
from discord.ext import commands
import os
import sys

# Comando RR para reiniciar o bot
@commands.command()
async def rr(ctx):
    if ctx.author.guild_permissions.administrator:
        await ctx.send(f"{ctx.bot.user.name} está reiniciando para updates.", delete_after=10)
        
        # Fechar o bot corretamente antes de reiniciar
        await ctx.bot.close()
        
        # Reiniciar o bot
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        await ctx.send("Você não tem permissão para usar este comando.", delete_after=10)
