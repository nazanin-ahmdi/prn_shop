#from config import *
#print(BOT_TOKEN)
#print(database)
#print(database_config)
#print(ADMIN_ID)
import telebot
from config import BOT_TOKEN
bot=telebot.TeleBot(BOT_TOKEN)
print('main bot:',id(bot))
