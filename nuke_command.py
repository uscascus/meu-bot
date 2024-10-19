import discord
from discord.ext import commands

# Função para verificar se o usuário tem permissão
def verificar_permissao(usuario, comando):
    return usuario.guild_permissions.administrator

# Comando Nuke para limpar o canal
@commands.command()
async def nuke(ctx):
    if verificar_permissao(ctx.author, 'nuke'):
        await ctx.channel.purge()
        await ctx.send("Canal limpo com sucesso!", delete_after=10)
    else:
        await ctx.send("Você não tem permissão para usar este comando.", delete_after=10)
