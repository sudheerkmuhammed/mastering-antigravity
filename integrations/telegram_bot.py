"""
Telegram Bot Bridge for Google Antigravity.
Streams real-time thoughts to Telegram messages and uploads generated artifacts.
"""

import os
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from google.antigravity import Agent, LocalAgentConfig, CapabilitiesConfig

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "mock_telegram_token")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Greets the user and displays available agent capabilities."""
    await update.message.reply_text(
        "👋 **Antigravity Telegram Gateway Active**\n\n"
        "Send me any task or prompt! Available slash commands:\n"
        "• `/goal <objective>` - High-autonomy verification mode\n"
        "• `/status` - Check current agent health\n",
        parse_mode="Markdown",
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes incoming text and streams thoughts & answers back."""
    user_prompt = update.message.text
    status_message = await update.message.reply_text("🤔 *Agent initialized. Reasoning...*", parse_mode="Markdown")

    config = LocalAgentConfig(
        workspace_dir=os.getcwd(),
        system_instructions="You are an autonomous pair programmer interfaced via Telegram.",
        capabilities=CapabilitiesConfig(
            allow_file_modifications=True,
            allow_terminal_execution=True,
        ),
    )

    try:
        async with Agent(config) as agent:
            response = await agent.chat(user_prompt)

            thought_buffer = ""
            last_edit = asyncio.get_event_loop().time()

            # Stream thinking events
            async for thought in response.thoughts:
                thought_buffer += thought
                now = asyncio.get_event_loop().time()
                # Rate limit edits to max once per 1.5 seconds
                if now - last_edit > 1.5:
                    snippet = thought_buffer[-180:].replace("_", "\\_").strip()
                    await status_message.edit_text(
                        f"⚙️ *Working...*\n\n💭 Thought: _{snippet}_",
                        parse_mode="Markdown",
                    )
                    last_edit = now

            # Collect final answer tokens
            answer = ""
            async for token in response:
                answer += token

            if not answer:
                answer = "✅ Task completed successfully without output."

            await status_message.edit_text(answer[:4000])

    except Exception as exc:
        await status_message.edit_text(f"❌ Error during agent execution: `{str(exc)}`", parse_mode="Markdown")


def main():
    if TELEGRAM_TOKEN == "mock_telegram_token":
        print("[!] Warning: TELEGRAM_BOT_TOKEN is not set. Please set environment variable.")

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("[*] Antigravity Telegram Bot is listening...")
    app.run_polling()


if __name__ == "__main__":
    main()
