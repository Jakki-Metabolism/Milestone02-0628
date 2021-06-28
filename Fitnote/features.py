from config import mysqlpassword
import pymysql
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext
from youtubesearchpython import VideosSearch


def check_table(tablename):
    conn = pymysql.connect(host='localhost',
                             user='root',
                             password=mysqlpassword,
                             database='bodydata')
    c = conn.cursor()
    c.execute("SELECT * FROM information_schema.tables WHERE table_schema = 'bodydata' AND table_name = '" + tablename +"'")
    result = c.fetchall()
    if len(result) == 0:
        query = "CREATE TABLE " + tablename + "(" + "username TEXT NOT NULL, weight FLOAT NOT NULL, height FLOAT NOT NULL)"
        c.execute(query)
        conn.commit()
    conn.close()

def check_history(tablename):
    conn = pymysql.connect(host='localhost',
                             user='root',
                             password=mysqlpassword,
                             database='calories')
    c = conn.cursor()
    c.execute("SELECT * FROM information_schema.tables WHERE table_schema = 'calories' AND table_name = '" + tablename +"'")
    result = c.fetchall()
    if len(result) == 0:
        query = "CREATE TABLE " + tablename + "(" + "id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT, username TEXT NOT NULL, time TEXT NOT NULL, intake FLOAT NOT NULL)"
        c.execute(query)
        conn.commit()
    conn.close()
#Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

#Start
def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_text("Hi " + update.message.from_user.first_name +
    " press /help for more info")

#Data
def see_data(update: Update, _: CallbackContext):
    conn = pymysql.connect(host='localhost',
                             user='root',
                             password=mysqlpassword,
                             database='bodydata')
    c = conn.cursor()

    chat_id = update.message.chat_id
    tablename = 'id' + str(chat_id)

    check_table(tablename)
    c.execute("SELECT * FROM " + tablename)
    rows = c.fetchall()
    conn.close()
    if len(rows) > 0:
        item1, item2 = rows[0][1], rows[0][2]
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
        tablename = 'id' + str(chat_id)
        username = query.from_user.username

        c.execute("SELECT * FROM " + tablename)
        rows = c.fetchall()
        conn.close()
        if len(rows) > 0:
            result = round(rows[0][1]/(rows[0][2]/100)**2,2)
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
        tablename = 'id' + str(chat_id)
        check_table(tablename)
        username = update.message.from_user.username

        weight = strings[0]
        height = strings[1]
        c.execute("DELETE FROM " + tablename)
        c.execute("INSERT INTO " + tablename + " VALUES('" + username + "','" + weight + "','" + height + "')")

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
    tablename = "id" + str(chat_id)
    username = update.message.from_user.username

    c.execute("SELECT * FROM " + tablename)
    rows = c.fetchall()
    conn.close()
    if len(rows) > 0:
        result = round(rows[0][1]/(rows[0][2]/100)**2,2)
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
        tablename = "id" + str(chat_id)
        check_history(tablename)
        username = update.message.from_user.username

        time = strings[0]
        intake = strings[1]
        c.execute("INSERT INTO " + tablename + " VALUES(DEFAULT, '" + username + "','" + time + "','" + intake +"')")

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
    tablename = "id" + str(chat_id)
    check_history(tablename)

    c.execute("SELECT * FROM " + tablename)
    rows = c.fetchall()
    conn.close()
    if len(rows) > 0:
        items = ""
        for row in rows:
            items += str(row[0]) + " " + str(row[2]) + " " + str(row[3]) + "\n"

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
    tablename = "id" + str(chat_id)
    check_history(tablename)
    c.execute("SELECT COUNT(*) FROM " + tablename)
    result = c.fetchall()

    if  int(result[0][0]) > 0:
        c.execute("DELETE FROM " + tablename)
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
        tablename = "id" + str(chat_id)
        check_history(tablename)

        id_intake = strings[0]
        c.execute("DELETE FROM " + tablename + " WHERE ID=" + id_intake)
        conn.commit()
        conn.close()
        update.message.reply_text("Successfully delete! ")
    else:
        update.message.reply_text("Syntax error. Press /help for more info")

#Recommend
def recommend(update: Update, _:CallbackContext):
    keywords = update.message.text.lower().split(" ")

    if len(keywords) >= 2:
        keywords.remove('/recommend')
        keystrings = ""
        for key in keywords:
            keystrings += key
    
        videosSearch = VideosSearch(keystrings, limit = 2)
        result = videosSearch.result()
        msg = result['result'][0]['link']
        update.message.reply_text(msg)
    else:
        update.message.reply_text("Syntax error. Press /help for more info")
#Help
def help(update: Update, _: CallbackContext) -> None:
    update.message.reply_text("⭕️ /see_my_data: see my body data\n"
                              "⭕️ /edit [weight] [height]: edit or add my body data; e.g /edit 50 160\n"
                              "⭕️ /bmi: calculate my BMI\n"
                              "⭕️ /add [yy-mm-dd] [calories]: Add a calories intake; e.g /add 21-06-21 160\n"
                              "⭕️ /show_list: to see my calories history\n"
                              "⭕️ /clear_list: clear my calories history\n"
                              "⭕️ /delete [ID]: delete an intake note\n"
                              "⭕️ /recommend [keywords]: recommend an exercise video\n")
