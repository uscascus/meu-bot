import discord
import json
import os
import asyncio
from discord.ext import commands

# Carregar o ID do canal de logs de um arquivo JSON
LOG_CHANNEL_FILE = 'log_channel.json'
if os.path.exists(LOG_CHANNEL_FILE):
    with open(LOG_CHANNEL_FILE, 'r') as f:
        log_channel_id = json.load(f).get('log_channel_id', None)
else:
    log_channel_id = None

# Carregar permissões de comandos do JSON
PERMISSOES_FILE = 'permissoes.json'
if os.path.exists(PERMISSOES_FILE):
    with open(PERMISSOES_FILE, 'r') as f:
        permissoes = json.load(f)
else:
    permissoes = {}

# Inicializar o bot para usar nas funções
def get_bot_instance():
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    return commands.Bot(command_prefix='!', intents=intents)

bot = get_bot_instance()

# Função para verificar permissões
def verificar_permissao(usuario, comando):
    if usuario.guild_permissions.administrator:
        return True  # Usuário é administrador, tem acesso a todos os comandos
    
    # Verificar permissões normais do cargo
    for cargo in usuario.roles:
        cargo_id = str(cargo.id)
        if cargo_id in permissoes and comando in permissoes[cargo_id]:
            return True
    return False

# Função para solicitar informações do usuário
async def solicitar_informacoes(ctx):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    # Solicitar ID do usuário
    await ctx.send("Por favor, insira o ID do usuário:", delete_after=30)
    try:
        user_msg = await ctx.bot.wait_for('message', check=check, timeout=60)
        user_id = int(user_msg.content)
        user = await ctx.bot.fetch_user(user_id)
    except (ValueError, asyncio.TimeoutError):
        await ctx.send("ID inválido ou tempo esgotado. Operação cancelada.", delete_after=30)
        return None, None, None

    # Solicitar motivo
    await ctx.send(f"Por favor, insira o motivo para a ação com {user.name}:", delete_after=30)
    try:
        reason_msg = await ctx.bot.wait_for('message', check=check, timeout=60)
        reason = reason_msg.content
    except asyncio.TimeoutError:
        await ctx.send("Tempo esgotado. Operação cancelada.", delete_after=30)
        return None, None, None

    # Solicitar link da imagem
    await ctx.send(f"Por favor, insira o link de imagem para o registro da ação com {user.name}:", delete_after=30)
    try:
        image_msg = await ctx.bot.wait_for('message', check=check, timeout=60)
        image_url = image_msg.content
    except asyncio.TimeoutError:
        await ctx.send("Tempo esgotado. Operação cancelada.", delete_after=30)
        return None, None, None

    return user, reason, image_url
