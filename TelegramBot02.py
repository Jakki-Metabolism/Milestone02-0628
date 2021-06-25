import pymysql

import logging
from telegram import (
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update
)
from telegram.bot import Bot
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    Filters,
    CallbackContext
)

token = "token"
mysqlpassword = "password"

#Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

#Start
def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_text("Hi " + update.message.from_user.first_name + " press /help for more info")

#Data
def see_data(update: Update, _: CallbackContext):
    conn = pymysql.connect(host='localhost',
                             user='root',
                             password=mysqlpassword,
                             database='bodydata')
    c = conn.cursor()

    chat_id = update.message.chat_id
    chat_id = str(chat_id)

    c.execute("SELECT * FROM BODYDATA WHERE CHAT_ID='" + chat_id + "'")
    rows = c.fetchall()
    conn.close()
    if len(rows) > 0:
        item1, item2 = rows[0][2], rows[0][3]
        username = update.message.from_user.username
        keyboard = [[InlineKeyboardButton("Edit My Data", callback_data='edit'),
                 InlineKeyboardButton("Calculate My BMI", callback_data='bmi')]]

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text("📄 " + username + "'s data:\n" + "weight: " + str(item1) + "\nheight: " + str(item2),
                                 reply_markup=reply_markup)
    else:
        update.message.reply_text("You haven't added your body data. Use /edit to add your data.")

def button(update: Update, _: CallbackContext) -> None:
    query = update.callback_query
    if format(query.data) == 'edit':
        query.edit_message_text("Please use /edit [your weight] [your height] to edit your information")
    if format(query.data) == 'bmi':
        conn = pymysql.connect(host='localhost',
                             user='root',
                             password=mysqlpassword,
                             database='bodydata')
        c = conn.cursor()

        chat_id = query.from_user.id
        chat_id = str(chat_id)
        username = query.from_user.username

        c.execute("SELECT * FROM BODYDATA WHERE CHAT_ID='" + chat_id + "'")
        rows = c.fetchall()
        conn.close()
        if len(rows) > 0:
            result = round(rows[0][2]/(rows[0][3]/100)**2,2)
            query.edit_message_text("📄 " + username + "'s bmi:\n" + str(result))
        else:
            query.edit_message_text("No data")

#Edit
def edit_data(update: Update, _: CallbackContext):
    strings = update.message.text.lower().split(" ")

    if len(strings) == 3:
        strings.remove('/edit')

        # Connecting to the SQL database
        conn = pymysql.connect(host='localhost',
                             user='root',
                             password=mysqlpassword,
                             database='bodydata')
        c = conn.cursor()

        chat_id = update.message.chat_id
        chat_id = str(chat_id)
        username = update.message.from_user.username

        weight = strings[0]
        height = strings[1]
        c.execute("DELETE FROM BODYDATA WHERE CHAT_ID = chat_id")
        c.execute("INSERT INTO BODYDATA VALUES('" + chat_id + "','" + username + "','" + weight + "','" + height +"')")

        conn.commit()
        conn.close()

        update.message.reply_text("You have edited your file successfully")
    else:
        update.message.reply_text("Syntax error. Press /help for more info")

#bmi
def bmi(update: Update, _:CallbackContext):
    conn = pymysql.connect(host='localhost',
                             user='root',
                             password=mysqlpassword,
                             database='bodydata')
    c = conn.cursor()

    chat_id = update.message.chat_id
    chat_id = str(chat_id)
    username = update.message.from_user.username

    c.execute("SELECT * FROM BODYDATA WHERE CHAT_ID='" + chat_id + "'")
    rows = c.fetchall()
    conn.close()
    if len(rows) > 0:
        result = round(rows[0][2]/(rows[0][3]/100)**2,2)
        username = update.message.from_user.username
        update.message.reply_text("📄 " + username + "'s bmi:\n" + str(result))
    else:
        update.message.reply_text("No body data")

#Add_intake
def add_intake(update: Update, _:CallbackContext):
    strings = update.message.text.lower().split(" ")

    if len(strings) == 3:
        strings.remove('/add')

        # Connecting to the SQL database
        conn = pymysql.connect(host='localhost',
                             user='root',
                             password=mysqlpassword,
                             database='calories')
        c = conn.cursor()

        chat_id = update.message.chat_id
        chat_id = str(chat_id)
        username = update.message.from_user.username

        time = strings[0]
        intake = strings[1]
        c.execute("INSERT INTO CALORIES VALUES(DEFAULT, '" + chat_id + "','" + username + "','" + time + "','" + intake +"')")

        conn.commit()
        conn.close()

        update.message.reply_text("Items are added to your list")
    else:
        update.message.reply_text("Syntax error. Press /help for more info")

#show_list
def show_list(update: Update, _:CallbackContext):
    conn = pymysql.connect(host='localhost',
                             user='root',
                             password=mysqlpassword,
                             database='calories')
    c = conn.cursor()

    chat_id = update.message.chat_id
    chat_id = str(chat_id)

    c.execute("SELECT * FROM CALORIES WHERE CHAT_ID='" + chat_id + "'")
    rows = c.fetchall()
    conn.close()
    if len(rows) > 0:
        items = ""
        for row in rows:
            items += str(row[0]) + " " + str(row[3]) + " " + str(row[4]) + "\n"

        username = update.message.from_user.username
        update.message.reply_text("📄 " + username + "'s list:\n" + "ID CreateTime Intake\n" + items)
    else:
        update.message.reply_text("No items in your list")

#clear_list
def clear_list(update: Update, _:CallbackContext):
    conn = pymysql.connect(host='localhost',
                             user='root',
                             password=mysqlpassword,
                             database='calories')
    c = conn.cursor()

    chat_id = update.message.chat_id
    chat_id = str(chat_id)

    if c.execute("DELETE FROM CALORIES WHERE CHAT_ID='" + chat_id + "'").rowcount > 0:
        conn.commit()
        update.message.reply_text("List delete successfully")
    else:
        update.message.reply_text("Nothing to delete")

    conn.close()

#delete_intake
def delete_intake(update: Update, _:CallbackContext):
    strings = update.message.text.lower().split(" ")

    if len(strings) == 2:
        strings.remove('/delete')

        # Connecting to the SQL database
        conn = pymysql.connect(host='localhost',
                             user='root',
                             password=mysqlpassword,
                             database='calories')
        c = conn.cursor()

        chat_id = update.message.chat_id
        chat_id = str(chat_id)

        id_intake = strings[0]
        c.execute("DELETE FROM CALORIES WHERE CHAT_ID='" + chat_id + "' AND ID=" + id_intake)
        conn.commit()
        conn.close()
        update.message.reply_text("Successfully delete! ")
    else:
        update.message.reply_text("Syntax error. Press /help for more info")


#Help
def help(update: Update, _: CallbackContext) -> None:
    update.message.reply_text("⭕️ /see_my_data: see my body data\n"
                              "⭕️ /edit [weight] [height]: edit or add my body data; e.g /edit 50 160\n"
                              "⭕️ /bmi: calculate my BMI\n"
                              "⭕️ /add [yy-mm-dd] [calories]: Add a calories intake; e.g /edit 21-06-21 160\n"
                              "⭕️ /show_list: to see my calories history\n"
                              "⭕️ /clear_list: clear my calories history\n"
                              "⭕️ /delete [ID]: delete an intake note\n"
                              "⭕️ /recomend: recommend an exercise video\n")
#The bot itself
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
    dispatcher.add_handler(CommandHandler('clear_list', show_list))
    dispatcher.add_handler(CommandHandler('delete', delete_intake))

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
