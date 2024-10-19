import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import os
import asyncio  # Importando asyncio para controle de timeout

PERMISSOES_FILE = 'permissoes.json'

# Inicialização da variável bot (para ser configurada pelo bot_main)
bot = None

# Função para definir o bot a partir do bot_main.py
def set_bot(b):
    global bot
    bot = b
    registrar_comandos()

# Função para salvar as permissões em um arquivo JSON
def salvar_permissoes(permissoes):
    with open(PERMISSOES_FILE, 'w') as f:
        json.dump(permissoes, f, indent=4)

# Função para carregar as permissões de um arquivo JSON, ou criar um novo
def carregar_permissoes():
    if os.path.exists(PERMISSOES_FILE):
        with open(PERMISSOES_FILE, 'r') as f:
            return json.load(f)
    else:
        return {}

# Função para registrar os comandos após o bot ser configurado
def registrar_comandos():
    @bot.command(name="registrar_permissao")  # Nome do comando alterado para "registrar_permissao"
    async def configurar_permissoes(ctx):
        permissoes = carregar_permissoes()

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        # Solicitar o ID do cargo
        await ctx.send("Por favor, insira o ID do cargo que você deseja configurar as permissões:", delete_after=60)
        try:
            cargo_msg = await bot.wait_for('message', check=check, timeout=60)
            cargo_id = str(cargo_msg.content)
        except asyncio.TimeoutError:
            await ctx.send("Tempo esgotado. Operação cancelada.", delete_after=30)
            return

        # Exemplo de comandos disponíveis para selecionar
        comandos_disponiveis = ['kick', 'ban', 'tempban', 'nuke', 'rr']
        
        # View para os botões de comandos
        class ComandosView(View):
            def __init__(self):
                super().__init__()
                self.selecionados = []

                # Criar um botão para cada comando
                for comando in comandos_disponiveis:
                    botao = Button(label=comando, style=discord.ButtonStyle.primary)
                    botao.callback = self.criar_callback(comando)
                    self.add_item(botao)

            def criar_callback(self, comando):
                async def callback(interaction):
                    if comando in self.selecionados:
                        self.selecionados.remove(comando)
                    else:
                        self.selecionados.append(comando)
                    await interaction.response.send_message(f"Comando {comando} {'adicionado' if comando in self.selecionados else 'removido'}!", ephemeral=True, delete_after=10)
                return callback

        # Enviar a mensagem com os botões
        view = ComandosView()
        await ctx.send("Selecione os comandos que o cargo pode utilizar:", view=view)

        # Aguardar a interação com os botões e salvar as permissões
        await asyncio.sleep(30)  # Tempo para interação (pode ajustar conforme necessário)
        
        if cargo_id not in permissoes:
            permissoes[cargo_id] = []
        
        permissoes[cargo_id].extend(view.selecionados)
        salvar_permissoes(permissoes)

        await ctx.send(f"Permissões configuradas para o cargo {cargo_id}: {', '.join(view.selecionados)}", delete_after=60)

# Carregar as permissões no início
permissoes = carregar_permissoes()
