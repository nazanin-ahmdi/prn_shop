from requests_forwarder import setup_proxy

setup_proxy(
    proxy_token="5f79369b2c80c570d05852cb912708d226a682f75a1f3f4dab96a1c4a1cc145c",
    hosts=["api.telegram.org"]
)

from main import bot

print("prn_bot started")
print("main bot:", id(bot))

import handlers

print("handlers imported")
print("bot has successfully started")

bot.infinity_polling()

