async def mensagens(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    mensagem = update.effective_message

    if not mensagem or not mensagem.text:
        return

    texto = normalizar_texto(mensagem.text)

    gatilhos_saudacao = [
        "oi",
        "ola",
        "bom dia",
        "boa tarde",
        "boa noite",
    ]

    gatilhos_pagamento = [
        "forma de pagamento",
        "formas de pagamento",
        "qual a forma de pagamento",
        "qual forma de pagamento",
        "como posso pagar",
        "como eu posso pagar",
        "pagamento",
    ]

    business_id = mensagem.business_connection_id

    # =====================================================
    # TELEGRAM BUSINESS
    # =====================================================

    if business_id:

        propria_loja = await mensagem_da_propria_loja(
            update,
            context
        )

        # -----------------------------------------------
        # MENSAGEM ENVIADA POR VOCÊ
        # -----------------------------------------------

        if propria_loja:

            if any(
                gatilho in texto
                for gatilho in gatilhos_pagamento
            ):
                await mostrar_pagamentos(
                    update,
                    context
                )

            return

        # -----------------------------------------------
        # MENSAGEM ENVIADA PELO CLIENTE
        # -----------------------------------------------

        if texto in gatilhos_saudacao:

            await enviar_mensagem(
                update,
                context,
                SAUDACAO
            )

        return

    # =====================================================
    # CONVERSA DIRETA COM O BOT
    # =====================================================

    if texto in gatilhos_saudacao:

        await enviar_mensagem(
            update,
            context,
            SAUDACAO
        )

        return

    if any(
        gatilho in texto
        for gatilho in gatilhos_pagamento
    ):

        await mostrar_pagamentos(
            update,
            context
        )

        return
