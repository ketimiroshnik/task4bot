import random

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, MessageHandler, Filters, ConversationHandler
from telegram.ext import CallbackContext, CommandHandler

TOKEN = '5749861245:AAHOOLyngTDLFdxpDHJeMEyuF2HOTTfIJ5c'


def get_data():
    global mas
    with open('data/words.txt', encoding='utf-8') as f:
        mas = [e.strip() for e in f.readlines()]


def start(update, context):
    global mas
    markup = ReplyKeyboardMarkup([["да", "нет"]], one_time_keyboard=True, resize_keyboard=True)
    update.message.reply_text("Привет! Я провожу тест по ударениям ЕГЭ")
    update.message.reply_text("Чтобы завершить тест дай команду /stop")
    update.message.reply_text("Готов пройти тестирование? (да/нет)", reply_markup=markup)
    context.user_data["right"] = 0
    context.user_data["count"] = 0
    context.user_data["mistakes"] = []
    context.user_data["ques"] = random.sample(mas, len(mas))
    return 1


def begin(update, context):
    markup = ReplyKeyboardMarkup([['/stop']], one_time_keyboard=False, resize_keyboard=True)
    res = update.message.text
    if res.lower() == 'да':
        update.message.reply_text("Отлично! Я буду отправлять словo, а ты мне в ответ - слово с ударением \n"
                                  "Вот тебе первое слово:\n" + context.user_data["ques"][0].lower(),
                                  reply_markup=markup)
        return 2
    elif res.lower() == 'нет':
        update.message.reply_text("Жаль. Тогда до встречи.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        update.message.reply_text("Я не понял твой ответ... Готов пройти тестирование? (да/нет)")
        return 1


def ques(update, context):
    res = update.message.text
    if res == context.user_data["ques"][0] or res == context.user_data["ques"][0].split()[0]:
        context.user_data["right"] += 1
        context.user_data["count"] += 1
        update.message.reply_text('+')
    else:
        context.user_data["count"] += 1
        context.user_data["mistakes"].append(context.user_data["ques"][0])
        update.message.reply_text(f'Ошибка! Правильный ответ - {context.user_data["ques"][0]}')
    del context.user_data["ques"][0]

    if not context.user_data["ques"]:
        return stop(update, context)
    update.message.reply_text('\n' + context.user_data["ques"][0].lower())
    return 2



def stop(update, context):
    if not context.user_data["count"]:
        update.message.reply_text(f'Тестирование завершено.', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    update.message.reply_text(f'Тестирование завершено. Балл {context.user_data["right"]} '
                              f' из {context.user_data["count"]}', reply_markup=ReplyKeyboardRemove())
    if context.user_data["mistakes"]:
        update.message.reply_text(f'Слова, в которых вы ошиблись:\n' + '\n'.join(context.user_data["mistakes"]))
    else:
        update.message.reply_text('Молодец, все идеально!')
    return ConversationHandler.END



def main():
    get_data()
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, pass_user_data=True)],

        states={
            2: [CommandHandler('stop', stop),
                MessageHandler(Filters.text, ques, pass_user_data=True)],
            1: [CommandHandler('stop', stop),
                MessageHandler(Filters.text, begin, pass_user_data=True)],
        },

        fallbacks=[CommandHandler('stop', stop)])
    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
