import os
import re
import threading
import unicodedata
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

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
# SERVIDOR WEB PARA O RENDER
# =========================================================

class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Gold PodZ Bot online")

    def log_message(self, format, *args):
        return


def iniciar_servidor_web():
    porta = int(os.environ.get("PORT", 10000))

    servidor = ThreadingHTTPServer(
        ("0.0.0.0", porta),
        HealthHandler
    )

    print(f"Servidor web iniciado na porta {porta}.")
    servidor.serve_forever()


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

async def mostrar_pagamentos(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

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

    # Funciona tanto para mensagem normal
    # quanto para Telegram Business
    if update.effective_message:
        await update.effective_message.reply_text(
            mensagem,
            reply_markup=markup
        )


# =========================================================
# /START
# =========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if update.effective_message:
        await update.effective_message.reply_text(SAUDACAO)


# =========================================================
# BOTÕES
# =========================================================

async def botoes(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    if not query:
        return

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
# MENSAGENS DOS CLIENTES
# NORMAL + TELEGRAM BUSINESS
# =========================================================

async def mensagens(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    mensagem = update.effective_message

    if not mensagem or not mensagem.text:
        return

    texto = normalizar_texto(mensagem.text)

    # -----------------------------------------------------
    # SAUDAÇÃO AUTOMÁTICA
    # -----------------------------------------------------
    #
    # Guarda quais clientes já receberam a saudação
    # enquanto o bot estiver rodando.
    #

    chat_id = mensagem.chat_id

    clientes_saudados = context.application.bot_data.setdefault(
        "clientes_saudados",
        set()
    )

    primeira_mensagem = chat_id not in clientes_saudados

    if primeira_mensagem:
        clientes_saudados.add(chat_id)

    # -----------------------------------------------------
    # GATILHOS DE PAGAMENTO
    # -----------------------------------------------------

    gatilhos_pagamento = [
        "forma de pagamento",
        "formas de pagamento",
        "qual a forma de pagamento",
        "qual forma de pagamento",
        "como posso pagar",
        "como eu posso pagar",
        "como pagar",
        "pagamento",
        "pagar",
    ]

    pediu_pagamento = any(
        gatilho in texto
        for gatilho in gatilhos_pagamento
    )

    # Se pediu pagamento, mostra o menu.
    # Se for a primeira mensagem, manda a saudação antes.

    if pediu_pagamento:

        if primeira_mensagem:
            await mensagem.reply_text(SAUDACAO)

        await mostrar_pagamentos(
            update,
            context
        )

        return

    # Primeira mensagem normal do cliente
    if primeira_mensagem:
        await mensagem.reply_text(SAUDACAO)


# =========================================================
# CONEXÃO TELEGRAM BUSINESS
# =========================================================

async def conexao_business(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    conexao = update.business_connection

    if not conexao:
        return

    if conexao.is_enabled:
        print(
            "Telegram Business conectado. "
            f"ID da conexão: {conexao.id}"
        )
    else:
        print("Telegram Business desconectado.")


# =========================================================
# INICIAR BOT
# =========================================================

def main():

    # ---------------------------------------------
    # Servidor web exigido pelo Render
    # ---------------------------------------------

    servidor = threading.Thread(
        target=iniciar_servidor_web,
        daemon=True
    )

    servidor.start()

    # ---------------------------------------------
    # Telegram
    # ---------------------------------------------

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

    # Mensagens normais e Business
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            mensagens
        )
    )

    # Registra alterações na conexão Business
    from telegram.ext import BusinessConnectionHandler

    app.add_handler(
        BusinessConnectionHandler(
            conexao_business
        )
    )

    print("Gold PodZ Bot iniciado com Telegram Business.")

    # Muito importante:
    # recebe também BUSINESS_MESSAGE e BUSINESS_CONNECTION
    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()
