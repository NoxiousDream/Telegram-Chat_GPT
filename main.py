import openai
import telebot
import os

dir_path = os.getcwd()


def parse_txt_to_dict_list(file_path, msg_id):
    with open(file_path, 'r') as file:
        content = file.read()
    lst = content.split(sep='3:zf')
    dict_list = []
    for line in lst:
        if line == "":
            continue
        parts = line.split('6453,')
        dictionary = {}
        for part in parts:
            key, value = part.split('543:')
            if key == "id" and msg_id:
                continue
            elif (key == 'role' or key == 'content') and not msg_id:
                continue
            dictionary.update({key: value})
        dict_list.append(dictionary)
    return dict_list


bot = telebot.TeleBot("ENTER YOUR TELEGRAM TOKEN")
openai.api_key = "ENTER YOUR CHAT-GPT TOKEN"


@bot.message_handler(commands=['start'])
def start(message):
    try:
        bot.send_message(message.chat.id, "Hi, " + message.chat.username + "!")
    except():  # If a user doesn't have Telegram username
        bot.send_message(message.chat.id, "Hi!")


@bot.message_handler(commands=['clear'])
def clear(message):
    messages = parse_txt_to_dict_list(dir_path + "/" + str(message.from_user.id) + ".txt", False)
    for message1 in messages:
        bot.delete_message(message.from_user.id, message1.get("id"))
    pass


@bot.message_handler(content_types=['text'])  # Ответ на сообщение
def get_text_messages(message):
    # creates file for user if there is none (works in Linux, not sure about Windows)
    # if not os.path.exists(dir_path + "/" + str(message.from_user.id) + ".txt"):
    #     subprocess.call("touch " + dir_path + "/" + str(message.from_user.id) + ".txt", shell=True)

    with open(dir_path + "/" + str(message.from_user.id) + ".txt", 'w+') as f:
        f.write('3:zfrole543:user6453,content543:' + message.text + "\n")

    # Genereting answer
    messages = parse_txt_to_dict_list(dir_path + "/" + str(message.from_user.id) + ".txt", True)
    chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, max_tokens=1000)
    reply = chat.choices[0].message.content
    sent1 = bot.send_message(message.chat.id, reply)

    # Adding to history to delete
    with open(dir_path + "/" + str(message.from_user.id) + ".txt", 'a') as f:
        f.write('3:zfrole543:assistant6453,content543:' + reply + "6453,id543:" + str(sent1.id) + "\n")


bot.polling(none_stop=True, interval=0)
