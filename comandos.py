import discord
from discord.ext import commands
import permissoes  # Importando o módulo permissoes para verificar permissões
from Loja import registrar_produto  # Importando o módulo de registro de produtos
import asyncio
# Função para verificar se o usuário tem permissão para usar o comando
def verificar_permissao(usuario, comando):
    if usuario.guild_permissions.administrator:
        return True  # Administradores têm acesso a todos os comandos
    # Verificar permissões personalizadas no módulo permissoes
    for role in usuario.roles:
        if str(role.id) in permissoes.permissoes and comando in permissoes.permissoes[str(role.id)]:
            return True
    return False

# Função que retorna a lista de comandos disponíveis
def listar_comandos():
    # Lista de comandos disponíveis no bot, incluindo os novos
    comandos = [
        "!kick - Expulsa um membro do servidor.",
        "!ban - Bane um membro do servidor.",
        "!tempban - Bane temporariamente um membro do servidor.",
        "!nuke - Limpa todas as mensagens do canal.",
        "!rr - Reinicia o bot.",
        "!registrarlog - Registra um canal para os logs.",
        "!registrar_permissao - Registra as permissões dos cargos.",
        "!comandos - Lista todos os comandos disponíveis.",
        "!registrar - Registra um produto na loja.",
        "!registrarcategoria - Registra a categoria onde os carrinhos serão criados.",
        "!comprar - Concede permissão temporária para acessar a loja.",
    ]
    return comandos

# Função que lista as permissões dos cargos
def listar_permissoes():
    permissoes_registradas = permissoes.permissoes
    permissoes_descricao = []
    for cargo_id, lista_comandos in permissoes_registradas.items():
        permissoes_descricao.append(f"Cargo ID: {cargo_id} - Permissões: {', '.join(lista_comandos)}")
    return permissoes_descricao

# Comando que exibe a lista de comandos
@commands.command()
async def comandos(ctx):
    if verificar_permissao(ctx.author, 'comandos'):
        lista_de_comandos = listar_comandos()
        embed = discord.Embed(title="Comandos Disponíveis", description="\n".join(lista_de_comandos), color=discord.Color.blue())
        await ctx.send(embed=embed)
    else:
        await ctx.send("Você não tem permissão para usar este comando.", delete_after=10)

# Comando que exibe as permissões dos cargos
@commands.command()
async def registrar_permissoes(ctx):
    if verificar_permissao(ctx.author, 'registrar_permissoes'):
        permissoes_descricao = listar_permissoes()
        if permissoes_descricao:
            embed = discord.Embed(title="Permissões dos Cargos", description="\n".join(permissoes_descricao), color=discord.Color.green())
            await ctx.send(embed=embed)
        else:
            await ctx.send("Nenhuma permissão registrada.", delete_after=10)
    else:
        await ctx.send("Você não tem permissão para usar este comando.", delete_after=10)

# Comando para registrar um produto na loja
@commands.command()
async def registrar(ctx):
    if verificar_permissao(ctx.author, 'registrar'):
        await registrar_produto.registrar(ctx)
    else:
        await ctx.send("Você não tem permissão para usar este comando.", delete_after=10)

# Comando para registrar a categoria onde os carrinhos serão criados
@commands.command()
async def registrarcategoria(ctx):
    if verificar_permissao(ctx.author, 'registrarcategoria'):
        await registrar_produto.registrarcategoria(ctx)
    else:
        await ctx.send("Você não tem permissão para usar este comando.", delete_after=10)

# Comando para dar permissão temporária para acessar a loja
@commands.command()
async def comprar(ctx):
    if verificar_permissao(ctx.author, 'comprar'):
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
    else:
        await ctx.send("Você não tem permissão para usar este comando.", delete_after=10)

# Adicionando os comandos ao bot
async def setup(bot):
    bot.add_command(comandos)
    bot.add_command(registrar_permissoes)
    bot.add_command(registrar)
    bot.add_command(registrarcategoria)
    bot.add_command(comprar)

