import requests
import hashlib
import random
import time
import telebot
from telebot import types

bot_token = "6391131503:AAHyE7biRkJSwhqsLCn1oTVkGsSy2NLndzM"

bot = telebot.TeleBot(bot_token)

PREFIX, NA, NUM_TIMES = range(3)

user_data = {}

def set_prefix(message):
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id, "Please enter the prefix (eg..+213):", reply_markup=markup)
    user_data[message.chat.id] = {'state': 'na'}
    bot.register_next_step_handler(message, set_na)

def set_na(message):
    prefix = message.text.strip()
    user_data[message.chat.id]['prefix'] = prefix
    bot.send_message(message.chat.id, "Enter the remaining digits of your phone number:\neg.\n0123456789")
    bot.register_next_step_handler(message, set_num_times)

def set_num_times(message):
    na = message.text.strip()
    user_data[message.chat.id]['na'] = na
    bot.send_message(message.chat.id, "Enter the number of times to send OTP:\nmax 3!! ")
    user_data[message.chat.id]['state'] = 'num_times'
    bot.register_next_step_handler(message, start_send_otp)

def start_send_otp(message):
    if message.text.strip() == "/start":
        handle_start(message)
        return
    
    num_times = int(message.text.strip())
    user_data[message.chat.id]['num_times'] = num_times
    prefix = user_data[message.chat.id].get('prefix')
    na = user_data[message.chat.id].get('na')
    
    if prefix and na and num_times:
        for _ in range(num_times):
            response = send_otp(prefix + na)
            bot.send_message(message.chat.id, response)
            time.sleep(30) 
        
        bot.send_message(message.chat.id, "OTP sent successfully!")
    else:
        bot.send_message(message.chat.id, "Please set prefix, remaining digits, and number of times first.")

def send_otp(phone_number):
    asa = '123456789'
    gigk = str(''.join(random.choice(asa) for i in range(10)))
    md5 = hashlib.md5(gigk.encode()).hexdigest()[:16]
    headers = {
        "Host": "account-asia-south1.truecaller.com",
        "content-type": "application/json; charset=UTF-8",
        "accept-encoding": "gzip",
        "user-agent": "Truecaller/12.34.8 (Android; 8.1.2)",
        "clientsecret": "lvc22mp3l1sfv6ujg83rd17btt"
    }
    url = "https://account-asia-south1.truecaller.com/v3/sendOnboardingOtp"
    m = phone_number
    data = '{"countryCode":"eg","dialingCode":20,"installationDetails":{"app":{"buildVersion":8,"majorVersion":12,"minorVersion":34,"store":"GOOGLE_PLAY"},"device":{"deviceId":"' + md5 + '","language":"ar","manufacturer":"Xiaomi","mobileServices":["GMS"],"model":"Redmi Note 8A Prime","osName":"Android","osVersion":"7.1.2","simSerials":["8920022021714943876f","8920022022805258505f"]},"language":"ar","sims":[{"imsi":"602022207634386","mcc":"602","mnc":"2","operator":"vodafone"},{"imsi":"602023133590849","mcc":"602","mnc":"2","operator":"vodafone"}],"storeVersion":{"buildVersion":8,"majorVersion":12,"minorVersion":34}},"phoneNumber":"' + m + '","region":"region-2","sequenceNo":1}'
    req = requests.post(url, headers=headers, data=data).text
    return req

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_data[message.chat.id] = {}  
    set_prefix(message)

@bot.message_handler(commands=['cancel'])
def handle_cancel(message):
    user_data.pop(message.chat.id, None)
    bot.send_message(message.chat.id, "Operation cancelled.")

bot.polling()
