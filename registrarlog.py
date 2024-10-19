import discord
from discord.ext import commands
import json
import os
import asyncio  # Importando asyncio para controle de timeout

LOG_CHANNEL_FILE = 'log_channel.json'

# Inicialização da variável bot (para ser configurada pelo bot_main)
bot = None

# Função para definir o bot a partir do bot_main.py
def set_bot(b):
    global bot
    bot = b
    registrar_comandos()

# Função para salvar o canal de logs em um arquivo JSON
def salvar_log_channel(channel_id):
    with open(LOG_CHANNEL_FILE, 'w') as f:
        json.dump({'log_channel_id': channel_id}, f, indent=4)

# Função para carregar o canal de logs de um arquivo JSON
def carregar_log_channel():
    if os.path.exists(LOG_CHANNEL_FILE):
        with open(LOG_CHANNEL_FILE, 'r') as f:
            return json.load(f).get('log_channel_id', None)
    else:
        return None

# Função para registrar os comandos após o bot ser configurado
def registrar_comandos():
    @bot.command()
    async def registrarlog(ctx):
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await ctx.send("Por favor, insira o ID do canal onde os logs serão enviados:", delete_after=60)
        try:
            canal_msg = await bot.wait_for('message', check=check, timeout=60)
            log_channel_id = int(canal_msg.content)
            salvar_log_channel(log_channel_id)
            await ctx.send(f"Canal de logs registrado com sucesso: {log_channel_id}", delete_after=60)
        except asyncio.TimeoutError:
            await ctx.send("Tempo esgotado. Operação cancelada.", delete_after=30)
        except ValueError:
            await ctx.send("ID de canal inválido. Operação cancelada.", delete_after=30)

    # Evento para registrar quem usou um comando
    @bot.event
    async def on_command(ctx):
        if log_channel_id:
            log_channel = bot.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(f"Comando `{ctx.command}` usado por {ctx.author} no canal {ctx.channel}.")

    # Evento para registrar edições de mensagens (exceto mensagens do bot)
    @bot.event
    async def on_message_edit(before, after):
        if log_channel_id:
            if before.author == bot.user:
                return  # Ignora edições feitas pelo próprio bot
            log_channel = bot.get_channel(log_channel_id)
            if log_channel and before.content != after.content:
                await log_channel.send(f"Mensagem editada por {before.author} no canal {before.channel}.\n"
                                       f"Antes: {before.content}\nDepois: {after.content}")

    # Evento para registrar deleções de mensagens (exceto mensagens do bot)
    @bot.event
    async def on_message_delete(message):
        if log_channel_id:
            if message.author == bot.user:
                return  # Ignora deleções feitas pelo próprio bot
            log_channel = bot.get_channel(log_channel_id)
            if log_channel:
                await log_channel.send(f"Mensagem deletada por {message.author} no canal {message.channel}.\n"
                                       f"Conteúdo da mensagem: {message.content}")

# Carregar o canal de logs ao iniciar
log_channel_id = carregar_log_channel()
