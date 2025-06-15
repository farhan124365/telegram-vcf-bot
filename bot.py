import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = os.getenv("7035411312:AAF0XgixqKJ6qjtULAwj7zShTSaGihtNU_0")
ALLOWED_USERS = [int(i) for i in os.getenv("7531273830").split(",")]

def txt_to_vcf(txt_content):
    vcf = ""
    for line in txt_content.splitlines():
        if line.strip() == '':
            continue
        parts = line.strip().split(',')
        name_part = parts[0].split(':')[1].strip()
        phone_part = parts[1].split(':')[1].strip()

        vcf += "BEGIN:VCARD\n"
        vcf += "VERSION:3.0\n"
        vcf += f"N:{name_part};;;;\n"
        vcf += f"FN:{name_part}\n"
        vcf += f"TEL;TYPE=CELL:{phone_part}\n"
        vcf += "END:VCARD\n\n"
    return vcf

def restricted(func):
    def wrapper(update: Update, context: CallbackContext):
        user_id = update.effective_user.id
        if user_id not in ALLOWED_USERS:
            update.message.reply_text("❌ You are not authorized to use this bot.")
            return
        return func(update, context)
    return wrapper

@restricted
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome! Send me a TXT file to convert to VCF.")

@restricted
def handle_document(update: Update, context: CallbackContext):
    file = update.message.document.get_file()
    file_path = file.download()

    with open(file_path, 'r') as f:
        txt_content = f.read()

    vcf_content = txt_to_vcf(txt_content)

    vcf_file_path = "output.vcf"
    with open(vcf_file_path, 'w') as vcf_file:
        vcf_file.write(vcf_content)

    update.message.reply_document(document=open(vcf_file_path, 'rb'))

    os.remove(file_path)
    os.remove(vcf_file_path)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document.mime_type("text/plain"), handle_document))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
