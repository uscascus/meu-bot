import discord
from discord.ext import commands
import asyncio

# Função auxiliar para solicitar o ID do usuário e o motivo
async def solicitar_informacoes(ctx):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    # Solicitar ID do usuário
    await ctx.send("Por favor, insira o ID do usuário que você deseja expulsar:", delete_after=60)
    try:
        user_msg = await ctx.bot.wait_for('message', check=check, timeout=60)
        user_id = int(user_msg.content)
        user = await ctx.guild.fetch_member(user_id)
    except (ValueError, asyncio.TimeoutError):
        await ctx.send("ID inválido ou tempo esgotado. Operação cancelada.", delete_after=30)
        return None, None

    # Solicitar motivo
    await ctx.send(f"Por favor, insira o motivo para expulsar {user.name}:", delete_after=60)
    try:
        reason_msg = await ctx.bot.wait_for('message', check=check, timeout=60)
        reason = reason_msg.content
    except asyncio.TimeoutError:
        await ctx.send("Tempo esgotado. Operação cancelada.", delete_after=30)
        return None, None

    return user, reason

# Comando Kick
@commands.command()
async def kick(ctx):
    if ctx.author.guild_permissions.kick_members:
        user, reason = await solicitar_informacoes(ctx)
        if user is None:
            return  # Se a operação foi cancelada ou houve erro, interromper

        await user.kick(reason=reason)
        await ctx.send(f"{user.name} foi expulso por {ctx.author} pelo motivo: {reason}.", delete_after=30)
    else:
        await ctx.send("Você não tem permissão para usar este comando.", delete_after=10)
