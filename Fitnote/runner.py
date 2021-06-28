from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from config import token, mysqlpassword
from features import *

def main() -> None:
    updater = Updater(token)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('See_my_data', see_data))
    dispatcher.add_handler(CallbackQueryHandler(button))
    dispatcher.add_handler(CommandHandler('edit', edit_data))
    dispatcher.add_handler(CommandHandler('bmi', bmi))
    dispatcher.add_handler(CommandHandler('add', add_intake))
    dispatcher.add_handler(CommandHandler('show_list', show_list))
    dispatcher.add_handler(CommandHandler('clear_list', clear_list))
    dispatcher.add_handler(CommandHandler('delete', delete_intake))
    dispatcher.add_handler(CommandHandler('recommend', recommend))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
