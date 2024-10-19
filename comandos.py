import discord
from discord.ext import commands
import permissoes  # Importando o módulo permissoes para verificar permissões

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
    # Lista de comandos disponíveis no bot
    comandos = [
        "!kick - Expulsa um membro do servidor.",
        "!ban - Bane um membro do servidor.",
        "!tempban - Bane temporariamente um membro do servidor.",
        "!nuke - Limpa todas as mensagens do canal.",
        "!rr - Reinicia o bot.",
        "!registrarlog - Registra um canal para os logs.",
        "!registrar_permissao - Registra as permissões dos cargos.",
        "!comandos - Lista todos os comandos disponíveis.",
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
