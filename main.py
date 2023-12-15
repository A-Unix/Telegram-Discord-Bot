#!/usr/bin/python3

import os
import discord
import subprocess
import time
from discord.ext import commands
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

try:
    from colorama import init, Fore
except ImportError:
    print(Fore.Red + "Colorama is not installed. Installing it...")
    subprocess.run(["pip", "install", "colorama"], check=True)
    from colorama import init, Fore

# Initialize colorama
init(autoreset=True)

# Clear the terminal screen
os.system("clear")

time.sleep(1)

print("\nWelcome!\n")

time.sleep(2)

TELEGRAM_BOT_TOKEN = input(Fore.CYAN + 'Please enter your Telegram bot token here: ')
DISCORD_BOT_TOKEN = input(Fore.LIGHTYELLOW_EX + 'Please enter your Discord bot token here: ')
DISCORD_CHANNEL_ID = input(Fore.GREEN + 'Please enter your Discord channel ID here: ')

tickets = {}

def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    context.user_data['ticket_open'] = False

    update.message.reply_text(Fore.LIGHTGREEN_EX + "Hello! Welcome to the support bot. Use /open_ticket to open a new ticket.")

def open_ticket(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    if context.user_data.get('ticket_open', False):
        update.message.reply_text(Fore.LIGHTRED_EX + "You already have an open ticket. Please close it before opening a new one.")
        return

    ticket_id = len(tickets) + 1
    tickets[ticket_id] = {'user_id': user_id, 'messages': []}
    context.user_data['ticket_open'] = True

    update.message.reply_text(Fore.LIGHTCYAN_EX + f"Ticket #{ticket_id} opened. You can now send your inquiries.")

def handle_ticket_message(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id

    if not context.user_data.get('ticket_open', False):
        update.message.reply_text(Fore.BLUE + "You don't have an open ticket. Use /open_ticket to open a new one.")
        return

    ticket_id = next((tid for tid, data in tickets.items() if data['user_id'] == user_id), None)

    if ticket_id is not None:
        tickets[ticket_id]['messages'].append(update.message.text)
        discord_channel.send(f"New message in Ticket #{ticket_id}: {update.message.text}")

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("open_ticket", open_ticket))
    dp.add_handler(MessageHandler(Filters.TEXT & ~Filters.COMMAND, handle_ticket_message))

    discord_bot = commands.Bot(command_prefix='!')

    @discord_bot.event
    async def on_ready():
        print(Fore.LIGHTYELLOW_EX + f'We have logged in as {discord_bot.user}')

    @discord_bot.event
    async def on_message(message):
        if message.author == discord_bot.user:
            return

        await message.author.send(Fore.LIGHTMAGENTA_EX + f"New message in Discord: {message.content}")

    try:
        discord_channel = discord_bot.get_channel(int(DISCORD_CHANNEL_ID))
    except (ValueError, AttributeError):
        print(Fore.LIGHTRED_EX + "Failed to retrieve Discord channel. Check the provided channel ID.")

    updater.start_polling()
    discord_bot.run(DISCORD_BOT_TOKEN)

if __name__ == '__main__':
    main()
