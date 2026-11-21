"""Telegram bot: answers simple health-centre questions using a small knowledge base + an LLM."""
import logging

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import (Application, CommandHandler, ContextTypes, MessageHandler,
                          filters)

from config import load_settings
from knowledge import load_chunks, top_chunks
from llm import LLMError, ask_llm
from rate_limit import RateLimiter

logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s",
                    level=logging.INFO)
log = logging.getLogger("phc-helper-bot")

TELEGRAM_MAX_CHARS = 4000
DISCLAIMER = ("\n\nThis is general information, not a doctor's advice. "
              "In an emergency call 108 or 112.")

settings = load_settings()
chunks = load_chunks()
limiter = RateLimiter(settings.rate_limit_messages, settings.rate_limit_window_seconds)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Namaste! I can answer simple health-centre questions, such as ORS, "
        "when to see a doctor, and basic first aid.\n\n"
        "Just type your question. For an emergency, call 108 or 112 right now." )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Type a short question, for example:\n"
        "- How do I make ORS?\n"
        "- When should I take a child with fever to the doctor?\n"
        "- What do I do if someone is not breathing?")


async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    question = (update.message.text or "").strip()

    if not limiter.allow(user_id):
        await update.message.reply_text("Please wait a minute before sending more questions.")
        return
    if len(question) > settings.max_input_chars:
        await update.message.reply_text(
            f"Please keep your question under {settings.max_input_chars} characters.")
        return

    await update.message.chat.send_action(ChatAction.TYPING)
    try:
        reply = await ask_llm(
            question, top_chunks(question, chunks),
            api_key=settings.openrouter_api_key, model=settings.model,
            max_input_chars=settings.max_input_chars,
            max_output_tokens=settings.max_output_tokens)
    except LLMError as exc:
        log.warning("LLM error for user %s: %s", user_id, exc)
        await update.message.reply_text(
            "Sorry, I could not answer right now. Please try again, or ask a health worker.")
        return

    log.info("answered user=%s question_len=%d", user_id, len(question))
    await update.message.reply_text((reply + DISCLAIMER)[:TELEGRAM_MAX_CHARS])


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.error("Unhandled error", exc_info=context.error)


def main() -> None:
    app = Application.builder().token(settings.telegram_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))
    app.add_error_handler(on_error)
    log.info("Bot started with %d knowledge chunks", len(chunks))
    app.run_polling()


if __name__ == "__main__":
    main()
