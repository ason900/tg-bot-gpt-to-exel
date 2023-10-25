import pandas as pd
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from io import BytesIO

# Создадим словарь для временного хранения данных пользователя
user_data = {}


# Обработчик команды /start
def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Привет! Отправь мне текстовую таблицу.")

    return 1


# Обработчик для ввода таблицы
def handle_text_table(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    text_table = update.message.text

    # Разделяем таблицу на строки
    table_lines = text_table.split('\n')

    # Определяем количество столбцов по первой строке (предполагается, что это заголовки)
    num_columns = len(
        table_lines[0].split('|')) - 2  # Вычитаем 2, так как строки начинаются и заканчиваются символом '|'

    # Разделяем строки на столбцы, используя определенное количество столбцов
    data = [line.split('|')[1:(num_columns + 1)] for line in table_lines if line.strip()]

    user_data[user_id] = {'data': data}

    # Создаем DataFrame
    df = pd.DataFrame(data, columns=[f'Column_{i}' for i in range(1, num_columns + 1)])

    # Экспортируем DataFrame в Excel
    output = BytesIO()
    df.to_excel(output, index=False, engine='xlsxwriter')
    output.seek(0)

    update.message.reply_document(document=output, filename='output.xlsx')

    return ConversationHandler.END


def main() -> None:
    token = '638077497:AAFH6k0lJx47ZAogh2dCv0TgbriSf_K6bb8'
    updater = Updater(token)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            1: [MessageHandler(Filters.text, handle_text_table)],
        },
        fallbacks=[],
    )
    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
