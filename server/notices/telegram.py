import datetime
import telebot

TOKEN = "828920359:AAGXTTWE64cTgeZLCsrqC9oZOo5bpemM7zo"
CHAT_ID = 240121526
TIME = datetime.datetime.now().strftime("%d %B %Y %I:%M")
bot = telebot.TeleBot(TOKEN)


def send_message(host, host_status, data):
    checks_data_string = '-------\n'
    for item in data:
        checks_data_string += '*{}* – {} – {} \n'.format(item, data[item]['status'], data[item]['value'])
    text = '-------\n*Time* {}\n*Host* {}\n*Status* {}\n'.format(TIME, host, host_status) + checks_data_string
    bot.send_message(CHAT_ID, text, parse_mode='Markdown')


if __name__ == '__main__':
    pass

