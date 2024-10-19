# tempban_command.py
from bot_instance import bot
from utils import verificar_permissao, solicitar_informacoes, log_channel_id
import asyncio

@bot.command()
async def tempban(ctx):
    if verificar_permissao(ctx.author, 'tempban'):
        user, reason, image_url = await solicitar_informacoes(ctx)
        if user is None:
            return
        guild = ctx.guild
        member = guild.get_member(user.id)
        if member is not None:
            await member.ban(reason=reason)
            await ctx.send(f"{member.name} foi temporariamente banido por 3 dias por {reason}.", delete_after=30)
            if log_channel_id:
                log_channel = bot.get_channel(log_channel_id)
                await log_channel.send(f"{member.name} foi temporariamente banido por {ctx.author} por 3 dias. Razão: {reason}. Imagem: {image_url}")

            # Aguarda 3 dias e depois desbane o usuário
            await asyncio.sleep(259200)  # 3 dias em segundos
            await guild.unban(user)
            await ctx.send(f"{user.name} foi desbanido após 3 dias.", delete_after=30)
            if log_channel_id:
                await log_channel.send(f"{user.name} foi desbanido após 3 dias.")
        else:
            await ctx.send("Usuário não encontrado no servidor.", delete_after=30)
    else:
        await ctx.send("Você não tem permissão para usar este comando.", delete_after=30)
