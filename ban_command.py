# ban_command.py
from bot_instance import bot
from utils import verificar_permissao, solicitar_informacoes, log_channel_id

@bot.command()
async def ban(ctx):
    if verificar_permissao(ctx.author, 'ban'):
        user, reason, image_url = await solicitar_informacoes(ctx)
        if user is None:
            return
        guild = ctx.guild
        member = guild.get_member(user.id)
        if member is not None:
            await member.ban(reason=reason)
            await ctx.send(f"{member.name} foi banido por {reason}.", delete_after=30)
            if log_channel_id:
                log_channel = bot.get_channel(log_channel_id)
                await log_channel.send(f"{member.name} foi banido por {ctx.author}. Razão: {reason}. Imagem: {image_url}")
        else:
            await ctx.send("Usuário não encontrado no servidor.", delete_after=30)
    else:
        await ctx.send("Você não tem permissão para usar este comando.", delete_after=30)
