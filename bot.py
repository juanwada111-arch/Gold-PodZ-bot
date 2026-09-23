import os
import re
import unicodedata

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)


# =========================================================
# CONFIGURAÇÕES
# =========================================================

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "Token não encontrado. Configure TELEGRAM_BOT_TOKEN "
        "nas variáveis de ambiente."
    )


# =========================================================
# TEXTOS
# =========================================================

SAUDACAO = """
👋 Olá, excelente dia!

Como posso ajudá-lo?
"""


PIX = """
💠 PAGAMENTO VIA PIX

Recebedor:
CM APOIO ADMINISTRATIVO

Chave PIX (CNPJ):
62.114.975/0001-06

Copie a chave acima e cole no aplicativo do seu banco para realizar o pagamento.

✅ Após realizar o pagamento, por favor envie o comprovante aqui no chat para confirmarmos.
"""


CARTAO_CREDITO = """
💳 PAGAMENTO NO CRÉDITO

O pagamento será realizado na maquininha no momento da entrega.

Após selecionar essa opção, é só aguardar o atendimento.
"""


CARTAO_DEBITO = """
💳 PAGAMENTO NO DÉBITO

O pagamento será realizado na maquininha no momento da entrega.

Após selecionar essa opção, é só aguardar o atendimento.
"""


DINHEIRO = """
💵 PAGAMENTO EM DINHEIRO

O pagamento será realizado no momento da entrega.

Se precisar de troco, por favor informe para qual valor precisa de troco, para levarmos o valor correto.
"""


# =========================================================
# FUNÇÕES AUXILIARES
# =========================================================

def normalizar_texto(texto):
    """
    Remove acentos, pontuação e diferenças entre
    maiúsculas/minúsculas para facilitar os gatilhos.
    """

    texto = texto.lower().strip()

    texto = unicodedata.normalize("NFD", texto)

    texto = "".join(
        caractere
        for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )

    texto = re.sub(r"[^\w\s]", "", texto)

    texto = re.sub(r"\s+", " ", texto)

    return texto


# =========================================================
# MENU DE PAGAMENTO
# =========================================================

async def mostrar_pagamentos(update: Update, context: ContextTypes.DEFAULT_TYPE):

    teclado = [

        [
            InlineKeyboardButton(
                "💠 PIX",
                callback_data="pix"
            )
        ],

        [
            InlineKeyboardButton(
                "💳 CARTÃO",
                callback_data="cartao"
            )
        ],

        [
            InlineKeyboardButton(
                "💵 DINHEIRO",
                callback_data="dinheiro"
            )
        ]
    ]

    markup = InlineKeyboardMarkup(teclado)

    mensagem = (
        "💳 FORMAS DE PAGAMENTO\n\n"
        "Como deseja realizar o pagamento?"
    )

    if update.message:

        await update.message.reply_text(
            mensagem,
            reply_markup=markup
        )

    elif update.callback_query:

        await update.callback_query.message.reply_text(
            mensagem,
            reply_markup=markup
        )


# =========================================================
# /START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(SAUDACAO)


# =========================================================
# BOTÕES
# =========================================================

async def botoes(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()


    # ---------------- PIX ----------------

    if query.data == "pix":

        await query.message.reply_text(PIX)


    # ---------------- CARTÃO ----------------

    elif query.data == "cartao":

        teclado = [

            [
                InlineKeyboardButton(
                    "💳 CRÉDITO",
                    callback_data="credito"
                )
            ],

            [
                InlineKeyboardButton(
                    "💳 DÉBITO",
                    callback_data="debito"
                )
            ],

            [
                InlineKeyboardButton(
                    "⬅️ VOLTAR",
                    callback_data="voltar_pagamento"
                )
            ]

        ]

        markup = InlineKeyboardMarkup(teclado)

        await query.message.reply_text(
            "💳 PAGAMENTO NO CARTÃO\n\n"
            "Qual modalidade deseja utilizar?",
            reply_markup=markup
        )


    # ---------------- CRÉDITO ----------------

    elif query.data == "credito":

        await query.message.reply_text(
            CARTAO_CREDITO
        )


    # ---------------- DÉBITO ----------------

    elif query.data == "debito":

        await query.message.reply_text(
            CARTAO_DEBITO
        )


    # ---------------- DINHEIRO ----------------

    elif query.data == "dinheiro":

        await query.message.reply_text(
            DINHEIRO
        )


    # ---------------- VOLTAR ----------------

    elif query.data == "voltar_pagamento":

        await mostrar_pagamentos(
            update,
            context
        )


# =========================================================
# GATILHOS POR TEXTO
# =========================================================

async def mensagens(update: Update, context: ContextTypes.DEFAULT_TYPE):

    texto = normalizar_texto(
        update.message.text
    )


    gatilhos_pagamento = [

        "forma de pagamento",

        "formas de pagamento",

        "qual a forma de pagamento",

        "qual forma de pagamento",

        "como posso pagar",

        "como eu posso pagar",

        "pagamento",
    ]


    # Verifica se a mensagem corresponde
    # a algum dos gatilhos

    if any(
        gatilho in texto
        for gatilho in gatilhos_pagamento
    ):

        await mostrar_pagamentos(
            update,
            context
        )


# =========================================================
# INICIAR BOT
# =========================================================

def main():

    app = Application.builder().token(TOKEN).build()


    # /start

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )


    # /pagamento

    app.add_handler(
        CommandHandler(
            "pagamento",
            mostrar_pagamentos
        )
    )


    # /formadepagamento

    app.add_handler(
        CommandHandler(
            "formadepagamento",
            mostrar_pagamentos
        )
    )


    # Botões

    app.add_handler(
        CallbackQueryHandler(
            botoes
        )
    )


    # Mensagens normais

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            mensagens
        )
    )


    print("Gold PodZ Bot iniciado.")

    app.run_polling()


if __name__ == "__main__":
    main()
