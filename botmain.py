import discord
from discord.ext import commands
import json
import os
import asyncio
from tokenboot import TOKEN

# Importando os comandos externos
from Loja import registrar_produto  # Certifique-se de que o caminho está correto

# Iniciando o bot
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Função para dar permissão ao cargo temporariamente
@bot.command()
async def comprar(ctx):
    cargo_id = 1296324846829043754  # ID do cargo a ser dado temporariamente
    cargo = discord.utils.get(ctx.guild.roles, id=cargo_id)

    if cargo is None:
        await ctx.send("Erro: Cargo não encontrado.")
        return

    try:
        # Adiciona o cargo ao usuário
        await ctx.author.add_roles(cargo)
        await ctx.send(f"O cargo `{cargo.name}` foi adicionado a você por 3 minutos. Aproveite para acessar os produtos.")

        # Aguarda 3 minutos (180 segundos)
        await asyncio.sleep(180)

        # Remove o cargo após 3 minutos
        await ctx.author.remove_roles(cargo)
        await ctx.send(f"O cargo `{cargo.name}` foi removido após 3 minutos.")

    except Exception as e:
        await ctx.send(f"Erro ao atribuir/remover o cargo: {e}")

# Função para carregar as extensões
async def load_extensions():
    try:
        await bot.load_extension('Loja.registrar_produto')
        print("Extensão 'registrar_produto' carregada com sucesso.")
    except Exception as e:
        print(f"Erro ao carregar extensão 'registrar_produto': {e}")

# Evento on_ready para recriar as views e carregar as extensões
@bot.event
async def on_ready():
    print(f'{bot.user.name} está online novamente!')

    # Recriar as views para produtos e carrinhos existentes
    if os.path.exists('produtos.json'):
        with open('produtos.json', 'r') as f:
            produtos = json.load(f)

        for produto_id, produto_data in produtos.items():
            mensagem_id = produto_data.get('mensagem_id')
            canal_texto_id = produto_data.get('canal_texto_id')
            if mensagem_id and canal_texto_id:
                try:
                    canal = bot.get_channel(canal_texto_id)
                    if isinstance(canal, discord.TextChannel):
                        mensagem = await canal.fetch_message(mensagem_id)

                        # Recriar os botões para interações persistentes
                        view_produto = registrar_produto.criar_view_produto(produto_id)
                        
                        await mensagem.edit(view=view_produto)

                        print(f"Views recriadas para o produto: {produto_data['nome']}")
                        await asyncio.sleep(2)  # Adicionar um intervalo para evitar rate limits
                    else:
                        print(f"Canal ID {canal_texto_id} não é um TextChannel. Produto: {produto_data['nome']}")
                except Exception as e:
                    print(f"Erro ao recriar view para o produto {produto_data['nome']}: {e}")

    # Carregar as extensões
    await load_extensions()

    # Chamada para recriar views em carrinhos
    await registrar_produto.carregar_views()

# Passar o bot para registrar_produto após sua inicialização
registrar_produto.set_bot(bot)

# Iniciando o bot com o token
bot.run(TOKEN)
