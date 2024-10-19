import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import os
import asyncio
import uuid  # Importado para gerar IDs únicos de compra

# Arquivo JSON onde os produtos são salvos
PRODUCTS_FILE = 'produtos.json'
CARRINHO_CATEGORIA_FILE = 'categoria_carrinho.json'  # Arquivo para armazenar a categoria dos carrinhos
USER_DATA_FILE = 'usuarios.json'  # Arquivo para armazenar os dados dos usuários

# Carregar os produtos já registrados
if os.path.exists(PRODUCTS_FILE):
    with open(PRODUCTS_FILE, 'r') as f:
        produtos = json.load(f)
else:
    produtos = {}

# Carregar os dados dos usuários
if os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, 'r') as f:
        usuarios = json.load(f)
else:
    usuarios = {}

# Dicionário para armazenar os carrinhos dos usuários
carts = {}

# Função para salvar os produtos no arquivo JSON
def salvar_produtos():
    with open(PRODUCTS_FILE, 'w') as f:
        json.dump(produtos, f, indent=4)

# Função para salvar os dados dos usuários no arquivo JSON
def salvar_usuarios():
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(usuarios, f, indent=4)

# Função para salvar os carrinhos dos usuários no arquivo JSON
def salvar_carrinhos():
    with open('carrinhos.json', 'w') as f:
        json.dump(carts, f, indent=4)

# Função auxiliar para checar se o usuário é administrador ou tem permissão especial
def checar_permissao(interaction):
    return interaction.user.guild_permissions.administrator or 'registrar_permissoes' in [role.name for role in interaction.user.roles]

# Função para criar a view de finalizar compra
def criar_view_finalizar_compra():
    view = View(timeout=None)
    finalizar_button = Button(label="Finalizar Compra", style=discord.ButtonStyle.green)

    async def finalizar_compra_callback(interaction: discord.Interaction):
        # Criar a mensagem de opções de recebimento
        embed_recebimento = discord.Embed(
            title="Forma de recebimento do(s) produto(s)",
            description="Escolha a forma que deseja receber seus produtos.\n\n"
                        "Lembre-se de conferir se está tudo correto:\n"
                        "• Caso DM, sua DM deve estar aberta para que eu possa te enviar.\n"
                        "• Caso WhatsApp, seu número precisa estar correto, confira bem!\n"
                        "• Caso E-mail, seu endereço de e-mail tem que estar certinho, preste atenção!",
            color=discord.Color.blue()
        )

        # Botões de escolha de recebimento
        view_recebimento = View()

        # Função para DM
        async def dm_callback(interaction: discord.Interaction):
            await interaction.response.send_message(f"Os produtos serão enviados para sua DM.", ephemeral=True)
            # Armazenar forma de recebimento
            usuario_id = str(interaction.user.id)
            if usuario_id not in usuarios:
                usuarios[usuario_id] = {}
            usuarios[usuario_id]['form_recebimento'] = 'DM'
            salvar_usuarios()
            # Prosseguir para método de pagamento
            await mostrar_metodo_pagamento(interaction)

        # Função para WhatsApp
        async def whatsapp_callback(interaction: discord.Interaction):
            await interaction.response.send_message(f"Os produtos serão enviados para seu WhatsApp.", ephemeral=True)
            # Armazenar forma de recebimento
            usuario_id = str(interaction.user.id)
            if usuario_id not in usuarios:
                usuarios[usuario_id] = {}
            usuarios[usuario_id]['form_recebimento'] = 'WhatsApp'
            salvar_usuarios()
            # Prosseguir para método de pagamento
            await mostrar_metodo_pagamento(interaction)

        # Função para Email
        async def email_callback(interaction: discord.Interaction):
            await interaction.response.send_message("Por favor, insira o seu e-mail para receber os produtos:", ephemeral=True)
            
            def check(m):
                return m.author == interaction.user and m.channel == interaction.channel
            
            try:
                email_msg = await interaction.client.wait_for('message', check=check, timeout=60)
                email = email_msg.content
                usuario_id = str(interaction.user.id)
                
                # Armazenar o e-mail no JSON de usuários
                if usuario_id not in usuarios:
                    usuarios[usuario_id] = {}
                usuarios[usuario_id]['email'] = email
                usuarios[usuario_id]['form_recebimento'] = 'Email'
                salvar_usuarios()

                await interaction.followup.send(f"E-mail armazenado com sucesso! Produtos serão enviados para o e-mail: {email}", ephemeral=True)

                # Prosseguindo para o próximo passo - Escolha de método de pagamento
                await mostrar_metodo_pagamento(interaction)

            except asyncio.TimeoutError:
                await interaction.followup.send("Tempo esgotado. Operação cancelada.", ephemeral=True)

        # Função para cancelar
        async def cancelar_callback(interaction: discord.Interaction):
            await interaction.response.send_message("Compra cancelada.", ephemeral=True)

        # Adicionar botões
        button_dm = Button(label="Mensagem via DM", style=discord.ButtonStyle.primary, emoji="💬")
        button_whatsapp = Button(label="Whatsapp", style=discord.ButtonStyle.success, emoji="📱")
        button_email = Button(label="E-mail", style=discord.ButtonStyle.secondary, emoji="✉️")
        button_cancel = Button(label="Cancelar", style=discord.ButtonStyle.danger)

        button_dm.callback = dm_callback
        button_whatsapp.callback = whatsapp_callback
        button_email.callback = email_callback
        button_cancel.callback = cancelar_callback

        view_recebimento.add_item(button_dm)
        view_recebimento.add_item(button_whatsapp)
        view_recebimento.add_item(button_email)
        view_recebimento.add_item(button_cancel)

        # Enviar a mensagem com as opções de recebimento
        await interaction.response.send_message(embed=embed_recebimento, view=view_recebimento, ephemeral=True)

    finalizar_button.callback = finalizar_compra_callback
    view.add_item(finalizar_button)

    return view

# Função para mostrar o método de pagamento
async def mostrar_metodo_pagamento(interaction: discord.Interaction):
    embed_pagamento = discord.Embed(
        title="Políticas de Venda",
        description=(
            "Todos os produtos disponíveis para compra em nosso Discord são digitais. "
            "Isso significa que, uma vez adquirido, o produto será entregue de forma eletrônica.\n\n"
            "Política de Reembolso e Devolução\n"
            "Devido à natureza digital dos nossos produtos, não oferecemos reembolsos ou devoluções após a conclusão da compra.\n\n"
            "Problemas Técnicos\n"
            "Se você encontrar algum problema técnico ao acessar ou utilizar o produto digital adquirido, "
            "nossa equipe de suporte está à disposição para ajudar a resolver qualquer questão.\n\n"
            "Aquisição Consciente\n"
            "Recomendamos que você leia todas as descrições dos produtos e revise todas as informações fornecidas antes de finalizar a compra."
        ),
        color=discord.Color.blue()
    )

    # Criar botões de escolha de método de pagamento
    view_pagamento = View()

    async def pix_callback(interaction: discord.Interaction):
        # Nova funcionalidade adicionada aqui
        usuario_id = str(interaction.user.id)
        if usuario_id not in usuarios or 'cart' not in usuarios[usuario_id]:
            await interaction.response.send_message("Seu carrinho está vazio.", ephemeral=True)
            return

        cart_items = usuarios[usuario_id]['cart']
        form_recebimento = usuarios[usuario_id].get('form_recebimento', 'Não especificado')
        purchase_id = str(uuid.uuid4())[:8]  # Gerar ID único de compra
        total_value = sum(item['valor_total'] for item in cart_items)

        # Criar embed com detalhes da compra
        embed_resumo = discord.Embed(
            title="Resumo da Compra",
            description=f"Forma de Recebimento: {form_recebimento}\nID da Compra: {purchase_id}\nValor Total: R$ {total_value}",
            color=discord.Color.green()
        )

        for item in cart_items:
            embed_resumo.add_field(
                name=item['nome_produto'],
                value=f"Preço Unitário: R$ {item['preco_unitario']}\nQuantidade: {item['quantidade']}\nValor: R$ {item['valor_total']}",
                inline=False
            )

        # Criar botões 'Gerar Pagamento' e 'Cancelar'
        view_confirmacao = View()
        button_gerar_pagamento = Button(label="Gerar Pagamento", style=discord.ButtonStyle.green)
        button_cancelar = Button(label="Cancelar", style=discord.ButtonStyle.red)

        async def gerar_pagamento_callback(interaction: discord.Interaction):
            await interaction.response.send_message("Pagamento gerado com sucesso!", ephemeral=True)
            # Aqui você pode adicionar a lógica para gerar o pagamento via Pix
            # Após o pagamento, limpar o carrinho
            usuarios[usuario_id]['cart'] = []
            salvar_usuarios()

        async def cancelar_callback(interaction: discord.Interaction):
            await interaction.response.send_message("Compra cancelada.", ephemeral=True)
            # Limpar o carrinho
            usuarios[usuario_id]['cart'] = []
            salvar_usuarios()

        button_gerar_pagamento.callback = gerar_pagamento_callback
        button_cancelar.callback = cancelar_callback

        view_confirmacao.add_item(button_gerar_pagamento)
        view_confirmacao.add_item(button_cancelar)

        await interaction.response.send_message(embed=embed_resumo, view=view_confirmacao, ephemeral=True)

    async def cartao_callback(interaction: discord.Interaction):
        await interaction.response.send_message("Você escolheu o método de pagamento via Cartão (Em desenvolvimento).", ephemeral=True)
        # Você pode adicionar lógica semelhante à do pix_callback aqui

    button_pix = Button(label="Pix", style=discord.ButtonStyle.success)
    button_cartao = Button(label="Cartão (Em desenvolvimento)", style=discord.ButtonStyle.secondary)
    
    button_pix.callback = pix_callback
    button_cartao.callback = cartao_callback

    view_pagamento.add_item(button_pix)
    view_pagamento.add_item(button_cartao)

    # Enviar a mensagem com as opções de pagamento
    await interaction.followup.send(embed=embed_pagamento, view=view_pagamento, ephemeral=True)

# Função para criar a view do produto (botões)
def criar_view_produto(produto_id):
    view = View(timeout=None)

    # Função de adicionar ao carrinho
    async def adicionar_carrinho(interaction: discord.Interaction):
        # Pegue o ID da categoria previamente registrada (a ser usada para os carrinhos)
        try:
            with open(CARRINHO_CATEGORIA_FILE, 'r') as f:
                categoria_dados = json.load(f)
            categoria_id = categoria_dados.get("categoria_id", None)
        except FileNotFoundError:
            await interaction.response.send_message("A categoria do carrinho não foi registrada ainda.", ephemeral=True)
            return

        if categoria_id is None:
            await interaction.response.send_message("Categoria do carrinho não encontrada.", ephemeral=True)
            return

        guild = interaction.guild
        categoria = discord.utils.get(guild.categories, id=categoria_id)

        if categoria is None:
            await interaction.response.send_message("Categoria não encontrada. Verifique o ID da categoria.", ephemeral=True)
            return

        # Verificar se o usuário já tem um carrinho (canal) existente
        existing_cart_channel = discord.utils.get(categoria.text_channels, name=f"carrinho-{interaction.user.name}")
        if existing_cart_channel:
            cart_channel = existing_cart_channel
        else:
            # Criar o canal de texto na categoria especificada
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            }

            # Criar um novo canal com o nome do usuário
            cart_channel = await guild.create_text_channel(f"carrinho-{interaction.user.name}", category=categoria, overwrites=overwrites)

        # Perguntar a quantidade de produtos
        await interaction.response.send_message("Por favor, insira a quantidade que deseja adicionar ao carrinho.", ephemeral=True)

        # Esperar a resposta do usuário
        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        try:
            quantidade_msg = await interaction.client.wait_for('message', check=check, timeout=60)
            quantidade = int(quantidade_msg.content)
        except (asyncio.TimeoutError, ValueError):
            await interaction.followup.send("Tempo esgotado ou valor inválido. Operação cancelada.", ephemeral=True)
            return

        # Dados do produto (use os dados reais aqui)
        produto = produtos[produto_id]  # Obter dados do produto
        nome_produto = produto['nome']
        preco_numerico = produto['preco_numerico']  # Usar o preço numérico cadastrado
        estoque = int(produto['estoque'])  # Verificar estoque do produto

        # Verificar se há estoque suficiente
        if quantidade > estoque:
            await interaction.followup.send(f"Estoque insuficiente! Apenas {estoque} unidades disponíveis.", ephemeral=True)
            return

        # Atualizar o estoque
        produtos[produto_id]['estoque'] = estoque - quantidade
        salvar_produtos()

        # Apagar a mensagem anterior
        canal = interaction.channel
        try:
            mensagem_produto = await canal.fetch_message(produto['mensagem_id'])
            await mensagem_produto.delete()
        except discord.errors.NotFound:
            await interaction.followup.send("Erro ao deletar a mensagem anterior.", ephemeral=True)

        cargo = produto['cargo']
        valor_total = preco_numerico * quantidade

        # Criar o embed do carrinho
        embed_carrinho = discord.Embed(
            title=f"Carrinho de {interaction.user.name}",  # Exibir o nome do usuário
            color=discord.Color.blue()
        )
        embed_carrinho.add_field(name="🛒 Produto", value=nome_produto, inline=True)
        embed_carrinho.add_field(name="💵 Preço unitário", value=f"R$ {preco_numerico}", inline=True)
        embed_carrinho.add_field(name="🔢 Quantidade", value=str(quantidade), inline=True)
        embed_carrinho.add_field(name="💰 Valor total", value=f"R$ {valor_total}", inline=True)
        embed_carrinho.add_field(name="🛡️ Você receberá o cargo", value=cargo, inline=True)
        embed_carrinho.set_thumbnail(url=produto['imagem'])
        embed_carrinho.set_footer(text="Developed by Uscascus")

        # Enviar a mensagem do carrinho no canal do carrinho
        view_finalizar = criar_view_finalizar_compra()
        cart_message = await cart_channel.send(embed=embed_carrinho, view=view_finalizar)

        # **Armazenar o ID da mensagem do carrinho para recriar a view posteriormente**
        usuario_id = str(interaction.user.id)
        if usuario_id not in usuarios:
            usuarios[usuario_id] = {}
        if 'cart_messages' not in usuarios[usuario_id]:
            usuarios[usuario_id]['cart_messages'] = []
        usuarios[usuario_id]['cart_messages'].append({
            'channel_id': cart_channel.id,
            'message_id': cart_message.id
        })
        salvar_usuarios()

        # Informar ao usuário que o produto foi adicionado ao carrinho
        await interaction.followup.send(f"O produto foi adicionado ao seu carrinho em {cart_channel.mention}.", ephemeral=True)

        # Armazenar o item no carrinho do usuário
        if 'cart' not in usuarios[usuario_id]:
            usuarios[usuario_id]['cart'] = []
        item = {
            'produto_id': produto_id,
            'nome_produto': nome_produto,
            'preco_unitario': preco_numerico,
            'quantidade': quantidade,
            'valor_total': valor_total
        }
        usuarios[usuario_id]['cart'].append(item)
        salvar_usuarios()

        # Reprintar o produto com o estoque atualizado
        embed_produto_atualizado = discord.Embed(title=produto['nome'], description=produto['descricao'])
        embed_produto_atualizado.add_field(name="💵 Preço", value=f"R$ {produto['preco']}", inline=True)
        embed_produto_atualizado.add_field(name="🛒 Estoque", value=produtos[produto_id]['estoque'], inline=True)
        embed_produto_atualizado.add_field(name="🛡️ Você receberá o cargo", value=produto['cargo'], inline=True)
        embed_produto_atualizado.set_image(url=produto['imagem'])
        embed_produto_atualizado.set_footer(text="Developed By Uscascus")

        nova_mensagem_produto = await canal.send(embed=embed_produto_atualizado)
        produtos[produto_id]['mensagem_id'] = nova_mensagem_produto.id
        salvar_produtos()

    # Função de editar o produto
    async def editar_produto(interaction: discord.Interaction):
        if not checar_permissao(interaction):
            await interaction.response.send_message("Você não tem permissão para editar.", ephemeral=True)
            return

        # Funções de callback para cada botão de edição
        async def alterar_nome(interaction):
            await interaction.response.send_message("Digite o novo nome:", ephemeral=True)
            try:
                nome_msg = await interaction.client.wait_for('message', check=lambda m: m.author == interaction.user, timeout=60)
                produtos[produto_id]['nome'] = nome_msg.content
                salvar_produtos()
            except asyncio.TimeoutError:
                await interaction.channel.send("Tempo esgotado para alterar o nome.")

        async def alterar_preco(interaction):
            await interaction.response.send_message("Digite o novo preço:", ephemeral=True)
            try:
                preco_msg = await interaction.client.wait_for('message', check=lambda m: m.author == interaction.user, timeout=60)
                produtos[produto_id]['preco'] = preco_msg.content
                salvar_produtos()
            except asyncio.TimeoutError:
                await interaction.channel.send("Tempo esgotado para alterar o preço.")

        async def alterar_estoque(interaction):
            await interaction.response.send_message("Digite o novo estoque:", ephemeral=True)
            try:
                estoque_msg = await interaction.client.wait_for('message', check=lambda m: m.author == interaction.user, timeout=60)
                produtos[produto_id]['estoque'] = estoque_msg.content
                salvar_produtos()
            except asyncio.TimeoutError:
                await interaction.channel.send("Tempo esgotado para alterar o estoque.")

        async def alterar_descricao(interaction):
            await interaction.response.send_message("Digite a nova descrição:", ephemeral=True)
            try:
                descricao_msg = await interaction.client.wait_for('message', check=lambda m: m.author == interaction.user, timeout=60)
                produtos[produto_id]['descricao'] = descricao_msg.content
                salvar_produtos()
            except asyncio.TimeoutError:
                await interaction.channel.send("Tempo esgotado para alterar a descrição.")

        async def alterar_imagem(interaction):
            await interaction.response.send_message("Digite o novo link da imagem:", ephemeral=True)
            try:
                imagem_msg = await interaction.client.wait_for('message', check=lambda m: m.author == interaction.user, timeout=60)
                produtos[produto_id]['imagem'] = imagem_msg.content
                salvar_produtos()
            except asyncio.TimeoutError:
                await interaction.channel.send("Tempo esgotado para alterar a imagem.")

        async def alterar_cargo(interaction):
            await interaction.response.send_message("Digite o novo cargo que o usuário receberá após a compra:", ephemeral=True)
            try:
                cargo_msg = await interaction.client.wait_for('message', check=lambda m: m.author == interaction.user, timeout=60)
                produtos[produto_id]['cargo'] = cargo_msg.content
                salvar_produtos()
            except asyncio.TimeoutError:
                await interaction.channel.send("Tempo esgotado para alterar o cargo.")

        async def deletar_produto(interaction):
            if not checar_permissao(interaction):
                await interaction.response.send_message("Você não tem permissão para deletar.", ephemeral=True)
                return

            try:
                # Deletar o produto
                canal = interaction.channel
                mensagem_produto = await canal.fetch_message(produtos[produto_id]['mensagem_id'])
                await mensagem_produto.delete()

                # Remover do JSON
                produtos.pop(produto_id)
                salvar_produtos()

                await interaction.response.send_message("Produto deletado com sucesso.", ephemeral=True)
            except discord.errors.NotFound:
                await interaction.response.send_message("Erro: A mensagem original não pôde ser encontrada para ser deletada.", ephemeral=True)

        async def finalizar_modificacoes(interaction):
            try:
                # Deletar o anúncio original
                canal = interaction.channel
                mensagem_produto = await canal.fetch_message(produtos[produto_id]['mensagem_id'])
                await mensagem_produto.delete()

                # Recriar o anúncio com as modificações
                novo_embed = discord.Embed(title=produtos[produto_id]['nome'], description=produtos[produto_id]['descricao'])
                novo_embed.add_field(name="💵 Preço", value=f"R$ {produtos[produto_id]['preco']}", inline=True)
                novo_embed.add_field(name="🛒 Estoque", value=produtos[produto_id]['estoque'], inline=True)
                novo_embed.add_field(name="🛡️ Você receberá o cargo", value=produtos[produto_id]['cargo'], inline=True)
                novo_embed.set_image(url=produtos[produto_id]['imagem'])
                novo_embed.set_footer(text="Developed By Uscascus")

                # Enviar o novo anúncio
                nova_mensagem_produto = await interaction.channel.send(embed=novo_embed)

                # Recriar os botões para o novo anúncio
                view_nova = criar_view_produto(produto_id)

                # Adicionar os botões ao novo anúncio
                await nova_mensagem_produto.edit(view=view_nova)

                # Atualizar o ID da nova mensagem no JSON
                produtos[produto_id]['mensagem_id'] = nova_mensagem_produto.id
                salvar_produtos()

            except discord.errors.NotFound:
                await interaction.response.send_message("Erro: A mensagem original não pôde ser encontrada para ser deletada.", ephemeral=True)

        # Criar os botões de modificação e deletar
        button_alterar_nome = Button(label="Alterar Nome", style=discord.ButtonStyle.blurple)
        button_alterar_nome.callback = alterar_nome

        button_alterar_preco = Button(label="Alterar Preço", style=discord.ButtonStyle.blurple)
        button_alterar_preco.callback = alterar_preco

        button_alterar_estoque = Button(label="Alterar Estoque", style=discord.ButtonStyle.blurple)
        button_alterar_estoque.callback = alterar_estoque

        button_alterar_descricao = Button(label="Alterar Descrição", style=discord.ButtonStyle.blurple)
        button_alterar_descricao.callback = alterar_descricao

        button_alterar_imagem = Button(label="Alterar Imagem", style=discord.ButtonStyle.blurple)
        button_alterar_imagem.callback = alterar_imagem

        button_alterar_cargo = Button(label="Alterar Cargo Recebido", style=discord.ButtonStyle.blurple)
        button_alterar_cargo.callback = alterar_cargo

        button_deletar = Button(label="Deletar Produto", style=discord.ButtonStyle.red)
        button_deletar.callback = deletar_produto

        button_finalizar = Button(label="Finalizar", style=discord.ButtonStyle.green, emoji="✔️")
        button_finalizar.callback = finalizar_modificacoes

        # Criando a view de modificação
        view_editar = View(timeout=30)
        view_editar.add_item(button_alterar_nome)
        view_editar.add_item(button_alterar_preco)
        view_editar.add_item(button_alterar_estoque)
        view_editar.add_item(button_alterar_descricao)
        view_editar.add_item(button_alterar_imagem)
        view_editar.add_item(button_alterar_cargo)
        view_editar.add_item(button_deletar)
        view_editar.add_item(button_finalizar)

        # Verificar se já foi respondido
        if interaction.response.is_done():
            await interaction.edit_original_response(view=view_editar)
        else:
            await interaction.response.send_message(view=view_editar, ephemeral=True)

    # Criar os botões iniciais
    button_add_cart = Button(label="Adicionar ao Carrinho", style=discord.ButtonStyle.green, emoji="🛒")
    button_config = Button(label="Configuração", style=discord.ButtonStyle.gray, emoji="⚙️")

    # Configurando ação dos botões
    button_add_cart.callback = adicionar_carrinho
    button_config.callback = editar_produto

    # Definir a view com os botões iniciais (sem os de edição)
    view.add_item(button_add_cart)
    view.add_item(button_config)

    return view

# Função para registrar o produto
@commands.command()
async def registrar(ctx):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    # Solicitar nome do produto
    await ctx.send("Por favor, insira o nome do produto:", delete_after=60)
    try:
        nome_msg = await ctx.bot.wait_for('message', check=check, timeout=60)
        nome = nome_msg.content
    except asyncio.TimeoutError:
        await ctx.send("Tempo esgotado. Operação cancelada.", delete_after=30)
        return

    # Solicitar preço
    await ctx.send("Por favor, insira o preço do produto:", delete_after=60)
    try:
        preco_msg = await ctx.bot.wait_for('message', check=check, timeout=60)
        preco = preco_msg.content
    except asyncio.TimeoutError:
        await ctx.send("Tempo esgotado. Operação cancelada.", delete_after=30)
        return

    # Solicitar preço numérico
    await ctx.send("Por favor, insira o preço numérico do produto (para cálculos):", delete_after=60)
    try:
        preco_numerico_msg = await ctx.bot.wait_for('message', check=check, timeout=60)
        preco_numerico = float(preco_numerico_msg.content)
    except (asyncio.TimeoutError, ValueError):
        await ctx.send("Valor inválido ou tempo esgotado. Operação cancelada.", delete_after=30)
        return

    # Solicitar estoque
    await ctx.send("Por favor, insira o estoque do produto:", delete_after=60)
    try:
        estoque_msg = await ctx.bot.wait_for('message', check=check, timeout=60)
        estoque = int(estoque_msg.content)
    except (asyncio.TimeoutError, ValueError):
        await ctx.send("Valor inválido ou tempo esgotado. Operação cancelada.", delete_after=30)
        return

    # Solicitar descrição
    await ctx.send("Por favor, insira a descrição do produto:", delete_after=60)
    try:
        descricao_msg = await ctx.bot.wait_for('message', check=check, timeout=60)
        descricao = descricao_msg.content
    except asyncio.TimeoutError:
        await ctx.send("Tempo esgotado. Operação cancelada.", delete_after=30)
        return

    # Solicitar cargo que recebe após a compra
    await ctx.send("Por favor, mencione o cargo que o usuário receberá após a compra:", delete_after=60)
    try:
        cargo_msg = await ctx.bot.wait_for('message', check=check, timeout=60)
        cargo = cargo_msg.content
    except asyncio.TimeoutError:
        await ctx.send("Tempo esgotado. Operação cancelada.", delete_after=30)
        return

    # Solicitar link da imagem
    await ctx.send("Por favor, insira o link da imagem do produto:", delete_after=60)
    try:
        imagem_msg = await ctx.bot.wait_for('message', check=check, timeout=60)
        imagem = imagem_msg.content
    except asyncio.TimeoutError:
        await ctx.send("Tempo esgotado. Operação cancelada.", delete_after=30)
        return

    # Solicitar tempo de expiração do produto
    await ctx.send("Por favor, insira em quantos dias o produto expira (ou 'nunca' se não expirar):", delete_after=60)
    try:
        expira_msg = await ctx.bot.wait_for('message', check=check, timeout=60)
        expira = expira_msg.content
    except asyncio.TimeoutError:
        await ctx.send("Tempo esgotado. Operação cancelada.", delete_after=30)
        return

    # Solicitar ID da categoria
    await ctx.send("Por favor, insira o ID da categoria onde o produto será registrado:", delete_after=60)
    try:
        categoria_id_msg = await ctx.bot.wait_for('message', check=check, timeout=60)
        categoria_id = int(categoria_id_msg.content)
    except (asyncio.TimeoutError, ValueError):
        await ctx.send("Valor inválido ou tempo esgotado. Operação cancelada.", delete_after=30)
        return

    # Armazenar o produto no dicionário
    produto_id = len(produtos) + 1
    produtos[produto_id] = {
        'nome': nome,
        'preco': preco,
        'preco_numerico': preco_numerico,
        'estoque': estoque,
        'descricao': descricao,
        'cargo': cargo,
        'imagem': imagem,
        'expira': expira,
        'categoria_id': categoria_id
    }

    # Salvar no arquivo JSON
    salvar_produtos()

    # Criar a sala na categoria com o nome do produto
    guild = ctx.guild
    categoria = discord.utils.get(guild.categories, id=categoria_id)
    if categoria:
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            discord.Object(id=1296324846829043754): discord.PermissionOverwrite(read_messages=True),  # Cargo necessário
            ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }
        channel = await guild.create_text_channel(nome, category=categoria, overwrites=overwrites)

        # Printar as informações do produto na sala criada
        embed = discord.Embed(title=nome, description=descricao)
        embed.add_field(name="💵 Preço", value=f"R$ {preco}", inline=True)
        embed.add_field(name="🛒 Estoque", value=estoque, inline=True)
        embed.add_field(name="🛡️ Você receberá o cargo", value=cargo, inline=True)
        embed.add_field(name="⏳ Expira de em:", value=expira, inline=True)
        embed.set_image(url=imagem)
        embed.set_footer(text="Developed By Uscascus")
        
        # Enviar a mensagem e armazenar para referência futura
        mensagem_produto = await channel.send(embed=embed)

        # **Armazenar o ID da mensagem**
        produtos[produto_id]['mensagem_id'] = mensagem_produto.id
        produtos[produto_id]['canal_texto_id'] = channel.id
        salvar_produtos()

        # Criar os botões para o novo produto
        view_produto = criar_view_produto(produto_id)
        await mensagem_produto.edit(view=view_produto)

    await ctx.send(f"O produto **{nome}** foi registrado com sucesso e a sala foi criada!", delete_after=30)

# Função para configurar o bot (para passar o objeto bot corretamente)
def set_bot(new_bot):
    global bot
    bot = new_bot

# Adicionando os comandos ao bot
async def setup(bot):
    bot.add_command(registrar)

# Comando para registrar a categoria onde os carrinhos serão criados
@commands.command()
async def registrarcategoria(ctx):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    await ctx.send("Por favor, insira o ID da categoria onde os carrinhos serão registrados:", delete_after=60)

    try:
        # Capturar o ID da categoria inserido pelo usuário
        categoria_id_msg = await ctx.bot.wait_for('message', check=check, timeout=60)
        categoria_id = int(categoria_id_msg.content)
        
        # Salvar o ID da categoria em um arquivo JSON
        with open(CARRINHO_CATEGORIA_FILE, 'w') as f:
            json.dump({"categoria_id": categoria_id}, f, indent=4)

        await ctx.send(f"Categoria de carrinho registrada com sucesso! ID: {categoria_id}")
    
    except (asyncio.TimeoutError, ValueError):
        await ctx.send("Valor inválido ou tempo esgotado. Operação cancelada.", delete_after=30)

# **Função para recarregar as views nos canais de carrinho quando o bot reinicia**
async def carregar_views():
    # Recarregar views nos produtos
    for produto_id, produto in produtos.items():
        if 'canal_texto_id' in produto and 'mensagem_id' in produto:
            try:
                view = criar_view_produto(produto_id)
                canal_id = produto['canal_texto_id']
                canal = bot.get_channel(canal_id)
                if canal:
                    msg = await canal.fetch_message(produto['mensagem_id'])
                    await msg.edit(view=view)
                    print(f"Views recriadas para o produto: {produto['nome']}")
                else:
                    print(f"Canal ID {canal_id} não encontrado.")
            except Exception as e:
                print(f"Erro ao recriar views para o produto {produto_id}: {e}")
        else:
            print(f"Produto ID {produto_id} não possui 'canal_texto_id' ou 'mensagem_id'. Pulando este produto.")
    
    # Recarregar views nos canais de carrinho
    for usuario_id, dados_usuario in usuarios.items():
        if 'cart_messages' in dados_usuario:
            for cart_msg in dados_usuario['cart_messages']:
                channel = bot.get_channel(cart_msg['channel_id'])
                if channel:
                    try:
                        message = await channel.fetch_message(cart_msg['message_id'])
                        view_finalizar = criar_view_finalizar_compra()
                        await message.edit(view=view_finalizar)
                        print(f"View recriada para o carrinho do usuário {usuario_id}")
                    except Exception as e:
                        print(f"Erro ao recriar view no carrinho: {e}")
