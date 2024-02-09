import telebot
import mysql.connector
import time

time.sleep(10)

mydb = mysql.connector.connect(
  host="mysql",
  user="app_user",
  password="1234",
  database="bot_db"
)

mycursor = mydb.cursor()

bot = telebot.TeleBot("6370601068:AAFPKPxW5VdQrjHUmsM8lxy8AxKeiQh_tlI")

mycursor.execute("CREATE TABLE IF NOT EXISTS users (id int auto_increment primary key, user_name varchar(50), user_id varchar(10))")
mydb.commit()
mycursor.execute("CREATE TABLE IF NOT EXISTS notes (id int auto_increment primary key, note_text varchar(200), note_time datetime, user_id varchar(10))")
mydb.commit()

print("Bot successfully started!")

def show_the_notes(notes_list: list):
    result_string = ""
    for index, item in enumerate(notes_list):
        result_string += f"Заметка #{index + 1}: \n{item[1]}\n\n"
    return result_string

def db_create_note(chatroom):
    try:
        sql = "INSERT INTO notes (note_text, note_time, user_id) VALUES ('%s', NOW(), '%s')" % (chatroom.text, chatroom.from_user.id)
        mycursor.execute(sql)
        mydb.commit()
        
        bot.reply_to(chatroom, "Данные успешно добавлены в базу данных!")

    except Exception as e:
        bot.reply_to(chatroom, f"create Ошибка: {e}")

def db_delete_note(chatroom):
    try:
        sql = "SELECT * FROM notes WHERE user_id=%s" % (chatroom.chat.id)
        mycursor.execute(sql)
        notes_list = mycursor.fetchall()
        print(notes_list)
        sql = "DELETE FROM notes WHERE user_id=%s AND id=%s" % (chatroom.chat.id, notes_list[int(chatroom.text) - 1][0])
        mycursor.execute(sql)
        mydb.commit()
        bot.reply_to(chatroom, "Заметка успешно удалена!")
    except Exception as e:
        bot.reply_to(chatroom, f"delete Ошибка: {e}")

@bot.message_handler(commands = ["start"])
def main(chatroom):
    mycursor.execute("""INSERT INTO users (user_name, user_id)
                        SELECT '%s', '%s'
                        FROM (SELECT 1) AS dummy
                        WHERE NOT EXISTS (
                            SELECT 1
                            FROM users
                            WHERE user_name = '%s' AND user_id = '%s'
                        )
                        LIMIT 1;
                     """ % (chatroom.from_user.first_name, chatroom.from_user.id, chatroom.from_user.first_name, chatroom.from_user.id))
    mydb.commit()
    bot.send_message(chatroom.chat.id, f"Hi {chatroom.from_user.first_name}! I'm ready to work!\n"
                                       "\n"
                                       "You can use this commands:\n"
                                       "\n"
                                       "To create a new note use /create\n"
                                       "To show ur notes use /show\n"
                                       "To delete the unnecessary note /delete\n")

@bot.message_handler(commands = ["hello"])
def main(chatroom):
    bot.send_message(chatroom.chat.id, "✌️")

@bot.message_handler(commands = ["create"])
def main(chatroom):
    bot.send_message(chatroom.chat.id, "Okay! Enter the note u want to save :)")
    bot.register_next_step_handler(chatroom, db_create_note)

@bot.message_handler(commands = ["show"])
def main(chatroom):
    try:
        # Выполнение SQL-запроса для добавления данных 
        sql = "SELECT * FROM notes WHERE user_id=%s" % (chatroom.from_user.id)
        mycursor.execute(sql)
        notes_list = mycursor.fetchall()
        if len(notes_list) == 0:
            bot.reply_to(chatroom, "U dont have notes yet")
        else:
            bot.reply_to(chatroom, "No problem. Lst of ur notes:")
            bot.send_message(chatroom.chat.id, show_the_notes(notes_list))

    except Exception as e:
        bot.reply_to(chatroom, f"show Ошибка: {e}")

@bot.message_handler(commands = ["delete"])
def main(chatroom):
    try:
        sql = "SELECT * FROM notes WHERE user_id=%s" % (chatroom.chat.id)
        mycursor.execute(sql)
        notes_list = mycursor.fetchall()

        if len(notes_list) == 0:
            bot.reply_to(chatroom, "U dont have notes yet")
        else:
            bot.send_message(chatroom.chat.id, "Huh, enter the number of note to delete")
            bot.register_next_step_handler(chatroom, db_delete_note)
            
        
    except Exception as e:
        bot.reply_to(chatroom, f"delete Ошибка: {e}")

@bot.message_handler()
def bad_command(chatroom):
    bot.reply_to(chatroom, "Sorry, i don't know this command :("
                                "\n"
                                "If you want to create a new note use /create")

bot.polling(none_stop=True)