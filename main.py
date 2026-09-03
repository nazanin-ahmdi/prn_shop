import os
import time
from collections import defaultdict, deque
from pathlib import Path
import telebot
from telebot import types
from telebot.types import (ReplyKeyboardMarkup,KeyboardButton,InlineKeyboardMarkup,InlineKeyboardButton,)
#from requests_forwarder import setup_proxy
from config import BOT_TOKEN, ADMIN_ID
from DQL import *
from DML import *
from catalog_images.catalog_images import get_product_image, get_category_image

#PROXY_TOKEN = os.getenv("PROXY_TOKEN")

#if PROXY_TOKEN:
 #   setup_proxy(
  #      proxy_token=PROXY_TOKEN,
   #     hosts=["api.telegram.org"]
    #)
#else:
 #   print("WARNING: PROXY_TOKEN not found. Direct Telegram connection will be used.")

bot = telebot.TeleBot(BOT_TOKEN)

SPAM_WINDOW = 5
SPAM_LIMIT = 6
SPAM_BLOCK_TIME = 30

message_history = defaultdict(deque)
spam_blocked_until = {}

def is_spam(cid):
    """Block users who send too many updates in a short time."""

    if cid == ADMIN_ID:
        return False
    now = time.time()

    blocked_until = spam_blocked_until.get(cid, 0)

    if now < blocked_until:
        return True

    history = message_history[cid]

    while history and now - history[0] > SPAM_WINDOW:
        history.popleft()

    history.append(now)

    if len(history) > SPAM_LIMIT:
        spam_blocked_until[cid] = now + SPAM_BLOCK_TIME
        history.clear()

        print(
            f"SPAM BLOCKED | user={cid} | "
            f"seconds={SPAM_BLOCK_TIME}"
        )

        return True
    return False


def anti_spam_message(message):
    return is_spam(message.from_user.id)

def anti_spam_callback(call):
    return is_spam(call.from_user.id)

BOT_COMMANDS = [
    types.BotCommand("start", "شروع ربات"),
    types.BotCommand("help", "راهنما"),
    types.BotCommand("menu", "منوی اصلی"),
    types.BotCommand("catalog", "مشاهده کاتالوگ"),
    types.BotCommand("contact", "تماس با ما"),
    types.BotCommand("admin", "پنل مدیریت"),
]

try:
    bot.set_my_commands(BOT_COMMANDS)
except Exception as error:
    print("امکان تنظیم دستورات ربات وجود نداشت:", error)

def main_menu():

    keyboard = ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=2
    )

    keyboard.add(
        KeyboardButton("🛍 محصولات"),
        KeyboardButton("🛒 سبد خرید"),
        KeyboardButton("📦 سفارش‌های من"),
        KeyboardButton("📚 کاتالوگ"),
        KeyboardButton("💳 اعتبار من"),
        KeyboardButton("☎️ تماس با ما"),
        KeyboardButton("🌐 زبان")
    )

    return keyboard

def product_inline_keyboard(product_id):

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "خرید",
            callback_data=f"buy_{product_id}"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "افزودن به سبد خرید",
            callback_data=f"add_{product_id}"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "بازگشت",
            callback_data="back_categories"
        )
    )

    return keyboard

def cart_item_keyboard(cart_id, quantity):

    keyboard = types.InlineKeyboardMarkup()

    keyboard.row(
        types.InlineKeyboardButton(
            "➖",
            callback_data=f"cart_dec_{cart_id}"
        ),
        types.InlineKeyboardButton(
            str(quantity),
            callback_data="cart_quantity"
        ),
        types.InlineKeyboardButton(
            "➕",
            callback_data=f"cart_inc_{cart_id}"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "حذف",
            callback_data=f"cart_remove_{cart_id}"
        )
    )

    return keyboard

def cart_checkout_keyboard():

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "تسویه حساب",
            callback_data="checkout"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "ادامه خرید",
            callback_data="back_categories"
        )
    )

    return keyboard
def orders_keyboard():

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "سفارش‌های من",
            callback_data="my_orders"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "ادامه خرید",
            callback_data="back_categories"
        )
    )

    return keyboard

def credit_keyboard():

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "افزایش اعتبار",
            callback_data="increase_credit"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "اعتبار من",
            callback_data="my_credit"
        )
    )

    return keyboard

def purchase_confirmation_keyboard(product_id):

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "تأیید خرید",
            callback_data=f"confirm_buy_{product_id}"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "لغو",
            callback_data="cancel_buy"
        )
    )

    return keyboard

print('handler bot:',id(bot))
@bot.message_handler(commands=["start"])
def start(message):

    if anti_spam_message(message):
        return

    print("دستور شروع اجرا شد")

    user = get_user_by_telegram_id(
        message.from_user.id
    )

    if user is None:

        register_user(message)

        user = get_user_by_telegram_id(
            message.from_user.id
        )

        create_wallet(user["id"])

    balance = get_wallet_balance(user["id"])

    bot.send_message(
        chat_id=message.chat.id,
        text=f""" 🌸 به فروشگاه PRN-Shop خوش آمدید.

لطفاً یکی از گزینه‌های زیر را انتخاب کنید.

اعتبار شما: {balance}


""",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: message.text == "🏠 خانه")
def home_handler(message):

    if anti_spam_message(message):
        return
    bot.send_message(
        message.chat.id,
        "🏠 منوی اصلی PRN-Shop",
        reply_markup=main_menu()
    )
# CART / ORDERS / CATALOG - MAIN MENU HANDLERS

def send_cart(chat_id, user_id):
    """Display the current user's shopping cart."""
    items = get_cart_items(user_id)

    if not items:
        bot.send_message(
            chat_id,
            "🛒 سبد خرید شما خالی است.",
            reply_markup=main_menu()
        )
        return

    total = 0

    bot.send_message(chat_id, "🛒 سبد خرید شما:")

    for item in items:
        subtotal = item["price"] * item["quantity"]
        total += subtotal

        text = (
            f"📦 {item['name']}\n"
            f"🔖 کد: {item['product_code']}\n"
            f"💰 قیمت واحد: {item['price']:,.2f}\n"
            f"🔢 تعداد: {item['quantity']}\n"
            f"💵 جمع: {subtotal:,.2f}"
        )

        bot.send_message(
            chat_id,
            text,
            reply_markup=cart_item_keyboard(
                item["cart_id"],
                item["quantity"]
            )
        )

    bot.send_message(
        chat_id,
        f"💰 مجموع سبد خرید: {total:,.2f}",
        reply_markup=cart_checkout_keyboard()
    )
@bot.message_handler(func=lambda message: message.text == "🛒 سبد خرید")
def cart_menu_handler(message):

    if anti_spam_message(message):
        return
    user = get_user_by_telegram_id(message.from_user.id)

    if user is None:
        bot.send_message(
            message.chat.id,
            "کاربر پیدا نشد.",
            reply_markup=main_menu()
        )
        return

    send_cart(message.chat.id, user["id"])

def send_my_orders(chat_id, user_id):
    """Display all completed/purchased orders of the current user."""
    orders = get_orders_by_user(user_id)

    if not orders:
        bot.send_message(
            chat_id,
            "📦 شما هنوز سفارشی ثبت نکرده‌اید.",
            reply_markup=main_menu()
        )
        return
    bot.send_message(chat_id, "📦 سفارش‌های من:")

    for order in orders:
        text = (
            f"🧾 شماره سفارش: {order['order_number']}\n"
            f"📌 وضعیت: {order['status']}\n"
            f"💰 مبلغ: {order['total_price']:,.2f}\n"
            f"📅 تاریخ: {order['created_at']}"
        )

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                "جزئیات سفارش",
                callback_data=f"order_{order['id']}"
            )
        )

        bot.send_message(
            chat_id,
            text,
            reply_markup=keyboard
        )

    bot.send_message(
        chat_id,
        "🏠 برای برگشت به منوی اصلی، گزینه «🏠 خانه» را بزنید.",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: message.text == "📦 سفارش‌های من")
def my_orders_menu_handler(message):

    if anti_spam_message(message):
        return
    user = get_user_by_telegram_id(message.from_user.id)

    if user is None:
        bot.send_message(
            message.chat.id,
            "کاربر پیدا نشد.",
            reply_markup=main_menu()
        )
        return

    send_my_orders(message.chat.id, user["id"])

def catalog_description(category_title):
    """Return a short catalog introduction for a category."""
    title = category_title.lower()

    if "پیستوله" in title or "pistol" in title or "gun" in title:
        return (
            "🔫 معرفی پیستوله\n\n"
            "پیستوله‌های این دسته برای پاشش رنگ و پوشش‌دهی در خطوط رنگ "
            "استفاده می‌شوند. مدل‌ها و مشخصات هر محصول در ادامه نمایش داده می‌شود."
        )

    if "پمپ" in title or "pump" in title:
        return (
            "⚙️ معرفی پمپ‌های دیافراگمی\n\n"
            "پمپ‌های دیافراگمی برای انتقال مواد و سیالات در سیستم‌های رنگ "
            "و تجهیزات صنعتی استفاده می‌شوند."
        )

    if "نازل" in title or "nozzle" in title:
        return (
            "🔧 معرفی نازل‌ها\n\n"
            "نازل‌ها در مدل‌ها و اندازه‌های مختلف برای کنترل و شکل‌دهی پاشش "
            "در تجهیزات رنگ مورد استفاده قرار می‌گیرند."
        )

    return (
        f"📚 کاتالوگ {category_title}\n\n"
        "در این بخش محصولات و توضیحات مربوط به این دسته را مشاهده می‌کنید."
    )

def catalog_keyboard(categories):
    keyboard = types.InlineKeyboardMarkup()

    for category in categories:
        keyboard.add(
            types.InlineKeyboardButton(
                category["title"],
                callback_data=f"catalog_category_{category['id']}"
            )
        )

    keyboard.add(
        types.InlineKeyboardButton(
            "🏠 خانه",
            callback_data="catalog_home"
        )
    )

    return keyboard

@bot.message_handler(func=lambda message: message.text == "📚 کاتالوگ")
def catalog_menu_handler(message):

    if anti_spam_message(message):
        return
    categories = get_categories()

    if not categories:
        bot.send_message(
            message.chat.id,
            "📚 هنوز دسته‌بندی‌ای برای کاتالوگ ثبت نشده است.",
            reply_markup=main_menu()
        )
        return

    bot.send_message(
        message.chat.id,
        "📚 کاتالوگ\n\n"
        "دسته‌بندی موردنظر را انتخاب کنید:",
        reply_markup=catalog_keyboard(categories)
    )


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("catalog_category_")
)
def catalog_category_handler(call):

    if anti_spam_callback(call):
        return
    category_id = int(call.data.split("_")[-1])

    categories = get_categories()
    category = next(
        (c for c in categories if c["id"] == category_id),
        None
    )

    if category is None:
        bot.answer_callback_query(call.id, "دسته‌بندی پیدا نشد.")
        return

    products = get_products_by_category(category["title"])

    bot.answer_callback_query(call.id)

    category_image = get_category_image(category["title"])

    if category_image:
        try:
            with open(category_image, "rb") as photo:
                bot.send_photo(
                    call.message.chat.id,
                    photo,
                    caption=catalog_description(category["title"])
                )
        except Exception as error:
            print("خطا در تصویر دسته‌بندی:", error)
            bot.send_message(
                call.message.chat.id,
                catalog_description(category["title"])
            )
    else:
        bot.send_message(
            call.message.chat.id,
            catalog_description(category["title"])
        )

    if not products:
        bot.send_message(
            call.message.chat.id,
            "در این دسته محصولی ثبت نشده است.",
            reply_markup=main_menu()
        )
        return

    for product in products:

        product_text = (
            f"📦 {product['name']}\n\n"
            f"🔖 کد: {product['product_code']}\n"
            f"📝 {product['description'] or 'توضیحی ثبت نشده است.'}\n"
        )

        image_path = get_product_image(
            product["product_code"]
        )

        if image_path:
            try:
                with open(image_path, "rb") as photo:
                    bot.send_photo(
                        call.message.chat.id,
                        photo,
                        caption=product_text
                    )
            except Exception as error:
                print("خطا در تصویر محصول:", error)
                bot.send_message(
                    call.message.chat.id,
                    product_text
                )
        else:
            bot.send_message(
                call.message.chat.id,
                product_text
            )

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            "📚 بازگشت به دسته‌بندی‌ها",
            callback_data="catalog_back"
        )
    )
    keyboard.add(
        types.InlineKeyboardButton(
            "🏠 خانه",
            callback_data="catalog_home"
        )
    )

    bot.send_message(
        call.message.chat.id,
        "یک گزینه را انتخاب کنید:",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data == "catalog_back")
def catalog_back(call):

    if anti_spam_callback(call):
        return
    categories = get_categories()

    bot.answer_callback_query(call.id)

    bot.send_message(
        call.message.chat.id,
        "📚 دسته‌بندی‌های کاتالوگ:",
        reply_markup=catalog_keyboard(categories)
    )

@bot.callback_query_handler(func=lambda call: call.data == "catalog_home")
def catalog_home(call):

    if anti_spam_callback(call):
        return
    bot.answer_callback_query(call.id)

    bot.send_message(
        call.message.chat.id,
        "🏠 منوی اصلی PRN-Shop",
        reply_markup=main_menu()
    )

@bot.message_handler(func=lambda message: message.text == "💳 اعتبار من")
def my_credit(message):

    if anti_spam_message(message):
        return

    user = get_user_by_telegram_id(
        message.from_user.id
    )

    if user is None:
        bot.send_message(
            message.chat.id,
            "❌ کاربر پیدا نشد."
        )
        return

    balance = get_wallet_balance(user["id"])

    bot.send_message(
        message.chat.id,
        f"اعتبار شما: {balance:,.2f}",
        reply_markup=credit_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == "🛍 محصولات")
def products(message):

    if anti_spam_message(message):
        return
    categories = get_categories()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for category in categories:
        markup.add(category["title"])

    bot.send_message(
        message.chat.id,
        "یک دسته بندی را انتخاب کنید.",
        reply_markup=markup
    )
@bot.message_handler(func=lambda message: any(
    message.text == category["title"] for category in get_categories()
))
def category_selected(message):

    if anti_spam_message(message):
        return

    products = get_products_by_category(message.text)

    if not products:
        bot.send_message(
            message.chat.id,
            "هیچ محصولی در این دسته‌بندی وجود ندارد."
        )
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for product in products:
        markup.add(product["name"])

    bot.send_message(
        message.chat.id,
        "یک محصول را انتخاب کنید.",
        reply_markup=markup
    )
@bot.message_handler(func=lambda message: get_product_by_name(message.text) is not None)
def product_selected(message):

    if anti_spam_message(message):
        return

    product = get_product_by_name(message.text)

   


    text = f"""
📦 نام محصول: {product['name']}

🔖 کد محصول: {product['product_code']}

💰 قیمت: {product['price']}

📦 موجودی: {product['stock']}

📝 توضیحات:

{product['description']}
"""

    bot.send_message(
    message.chat.id,
    text,
    reply_markup=product_inline_keyboard(product["id"])
    )
@bot.callback_query_handler(func=lambda call: call.data.startswith("add_"))
def add_product_to_cart(call):

    if anti_spam_callback(call):
        return

    product_id = int(call.data.split("_")[1])

    user = get_user_by_telegram_id(call.from_user.id)

    if user is None:
        bot.answer_callback_query(
            call.id,
            "❌ کاربر پیدا نشد."
        )
        return

    add_to_cart(
        user["id"],
        product_id
    )

    bot.answer_callback_query(
        call.id,
        "✅ محصول به سبد خرید اضافه شد."
    )
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            "مشاهده سبد خرید",
            callback_data="view_cart"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "ادامه خرید",
            callback_data="back_categories"
        )
    )
    bot.send_message(
        call.message.chat.id,
        "✅ محصول به سبد خرید اضافه شد.",
        reply_markup=keyboard
    )
@bot.callback_query_handler(func=lambda call: call.data == "view_cart")
def view_cart(call):

    if anti_spam_callback(call):
        return

    user = get_user_by_telegram_id(call.from_user.id)
    if user is None:
        bot.answer_callback_query(
            call.id,
            "❌ کاربر پیدا نشد."
        )
        return

    items = get_cart_items(user["id"])
    bot.answer_callback_query(call.id)
    if not items:

        bot.send_message(
            call.message.chat.id,
            "🛒 سبد خرید شما خالی است."
        )

        return

    bot.send_message(
        call.message.chat.id,
        "🛒 سبد خرید شما"
    )
    total = 0
    for item in items:

        subtotal = item["price"] * item["quantity"]

        total += subtotal

        text = (
            f"📦 {item['name']}\n"
            f"کد: {item['product_code']}\n"
            f"قیمت: {item['price']}\n"
            f"تعداد: {item['quantity']}\n"
            f"جمع جزء: {subtotal}"
        )

        bot.send_message(
            call.message.chat.id,
            text,
            reply_markup=cart_item_keyboard(
                item["cart_id"],
                item["quantity"]
            )
        )

    bot.send_message(
        call.message.chat.id,
        f"💰 مجموع: {total}",
        reply_markup=cart_checkout_keyboard()
    )
def refresh_cart_item(call, cart_id):

    item = get_cart_item(cart_id)
    if item is None:
        return
    subtotal = item["price"] * item["quantity"]

    text = (
        f"محصول: {item['name']}\n"
        f"کد: {item['product_code']}\n"
        f"قیمت: {item['price']}\n"
        f"تعداد: {item['quantity']}\n"
        f"جمع جزء: {subtotal}"
    )

    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=cart_item_keyboard(
            item["cart_id"],
            item["quantity"]
        )
    )
bot.callback_query_handler(
func=lambda call: call.data.startswith("cart_inc_")
)
def increase_cart_quantity(call):
    if anti_spam_callback(call):
        return
    cart_id = int(call.data.split("_")[2])
    item = get_cart_item(cart_id)

    if item is None:
        bot.answer_callback_query(
            call.id,
            "❌ مورد موردنظر در سبد خرید پیدا نشد."
        )
        return
    new_quantity = item["quantity"] + 1

    if new_quantity > item["stock"]:
        bot.answer_callback_query(
            call.id,
            "❌ موجودی کافی نیست."
        )
        return
    update_cart_quantity(
        cart_id,
        new_quantity
    )
    bot.answer_callback_query(
        call.id,
        "✅ تعداد افزایش یافت."
    )

    refresh_cart_item(call, cart_id)

@bot.callback_query_handler(
func=lambda call: call.data.startswith("cart_dec_")
)
def decrease_cart_quantity(call):

    if anti_spam_callback(call):
        return
    cart_id = int(call.data.split("_")[2])

    item = get_cart_item(cart_id)

    if item is None:
        bot.answer_callback_query(
            call.id,
            "❌ مورد موردنظر در سبد خرید پیدا نشد."
        )
        return
    new_quantity = item["quantity"] - 1
    if new_quantity <= 0:
        remove_from_cart(cart_id)

        bot.answer_callback_query(
            call.id,
            "✅ محصول از سبد خرید حذف شد."
        )

        bot.edit_message_text(
            "✅ محصول از سبد خرید حذف شد.",
            call.message.chat.id,
            call.message.message_id
        )

        return

    update_cart_quantity(
        cart_id,
        new_quantity
    )
    bot.answer_callback_query(
        call.id,
        "✅ تعداد کاهش یافت."
    )

    refresh_cart_item(call, cart_id)

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("cart_dec_")
)
def decrease_cart_quantity(call):

    cart_id = int(call.data.split("_")[2])
    item = get_cart_item(cart_id)

    if item is None:
        bot.answer_callback_query(
            call.id,
            "❌ مورد موردنظر در سبد خرید پیدا نشد."
        )
        return
    new_quantity = item["quantity"] - 1
    if new_quantity <= 0:
        remove_from_cart(cart_id)

        bot.answer_callback_query(
            call.id,
            "✅ محصول از سبد خرید حذف شد."
        )

        bot.edit_message_text(
            "✅ محصول از سبد خرید حذف شد.",
            call.message.chat.id,
            call.message.message_id
        )

        return
    update_cart_quantity(
        cart_id,
        new_quantity
    )
    bot.answer_callback_query(
        call.id,
        "✅ تعداد کاهش یافت."
    )

    refresh_cart_item(call, cart_id)

@bot.callback_query_handler(
    func=lambda call: call.data == "checkout"
)
def checkout(call):

    if anti_spam_callback(call):
        return
    user = get_user_by_telegram_id(call.from_user.id)
    if user is None:
        bot.answer_callback_query(
            call.id,
            "❌ کاربر پیدا نشد."
        )
        return
    items = get_cart_items(user["id"])
    if not items:
        bot.answer_callback_query(
            call.id,
            "🛒 سبد خرید شما خالی است."
        )
        return
    total = 0

    for item in items:
        total += item["price"] * item["quantity"]
    bot.answer_callback_query(call.id)

    text = (
        "تأیید سفارش\n\n"
        f"تعداد اقلام: {len(items)}\n"
        f"مجموع: {total}\n\n"
        "آیا می‌خواهید این سفارش را ثبت کنید؟"
    )

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            "تأیید سفارش",
            callback_data="confirm_order"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "لغو",
            callback_data="cancel_order"
        )
    )

    bot.send_message(
        call.message.chat.id,
        text,
        reply_markup=keyboard
    )
@bot.callback_query_handler(
    func=lambda call: call.data == "confirm_order"
)
def confirm_order(call):

    if anti_spam_callback(call):
        return
    user = get_user_by_telegram_id(call.from_user.id)
    if user is None:
        bot.answer_callback_query(
            call.id,
            "❌ کاربر پیدا نشد."
        )
        return
    user_id = user["id"]

    # Get current cart
    items = get_cart_items(user_id)

    if not items:

        bot.answer_callback_query(
            call.id,
            "🛒 سبد خرید شما خالی است."
        )

        bot.send_message(
            call.message.chat.id,
            "🛒 سبد خرید شما خالی است."
        )

        return

    total = 0

    for item in items:
        total += item["price"] * item["quantity"]

    # Check stock before creating order
    for item in items:

        if item["quantity"] > item["stock"]:

            bot.answer_callback_query(
                call.id,
                "❌ موجودی کافی نیست."
            )

            bot.send_message(
                call.message.chat.id,
                f"Not enough stock for {item['name']}."
            )

            return

    order_number = f"ORD-{int(time.time())}"

    order_id = insert_order(
        order_number,
        user_id,
        "pending",
        total,
        "",
        "سفارش تلگرامی"
    )
    for item in items:

        insert_order_item(
            order_id,
            item["product_id"],
            item["quantity"],
            item["price"]
        )
        decrease_product_stock(
            item["product_id"],
            item["quantity"]
        )
        remove_from_cart(
            item["cart_id"]
        )

    bot.answer_callback_query(
        call.id,
        "✅ سفارش تأیید شد."
    )

    bot.send_message(
        call.message.chat.id,
        f"""
Order successfully placed.

شماره سفارش: {order_number}

مجموع: {total}

Thank you for your purchase.
""",
reply_markup=orders_keyboard()
    )
def get_orders_by_user(user_id):

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
    SELECT
        id,
        order_number,
        status,
        total_price,
        address,
        description,
        created_at
    FROM orders
    WHERE user_id = %s
    ORDER BY id DESC
    """

    cur.execute(sql, (user_id,))

    orders = cur.fetchall()

    cur.close()
    conn.close()

    return orders
@bot.callback_query_handler(
    func=lambda call: call.data == "my_orders"
)
def my_orders(call):

    if anti_spam_callback(call):
        return

    user = get_user_by_telegram_id(call.from_user.id)

    if user is None:
        bot.answer_callback_query(
            call.id,
            "❌ کاربر پیدا نشد."
        )
        return

    orders = get_orders_by_user(user["id"])

    bot.answer_callback_query(call.id)

    if not orders:

        bot.send_message(
            call.message.chat.id,
            "📦 شما هنوز سفارشی ثبت نکرده‌اید."
        )

        return
    bot.send_message(
        call.message.chat.id,
        "سفارش‌های من"
    )
    for order in orders:

        text = (
            f"شماره سفارش: {order['order_number']}\n"
            f"وضعیت: {order['status']}\n"
            f"مجموع: {order['total_price']}\n"
            f"تاریخ: {order['created_at']}"
        )

        keyboard = types.InlineKeyboardMarkup()

        keyboard.add(
            types.InlineKeyboardButton(
                "مشاهده سفارش",
                callback_data=f"order_{order['id']}"
            )
        )

        bot.send_message(
            call.message.chat.id,
            text,
            reply_markup=keyboard
        )
@bot.callback_query_handler(
    func=lambda call: call.data.startswith("order_")
)
def view_order(call):

    if anti_spam_callback(call):
        return

    order_id = int(call.data.split("_")[1])

    user = get_user_by_telegram_id(call.from_user.id)

    if user is None:
        bot.answer_callback_query(
            call.id,
            "❌ کاربر پیدا نشد."
        )
        return
    orders = get_orders_by_user(user["id"])
    order = None
    for item in orders:
        if item["id"] == order_id:
            order = item
            break

    if order is None:

        bot.answer_callback_query(
            call.id,
            "❌ سفارش پیدا نشد."
        )
        return

    items = get_order_items(order_id)
    bot.answer_callback_query(call.id)
    text = (
        f"Order Details\n\n"
        f"شماره سفارش: {order['order_number']}\n"
        f"وضعیت: {order['status']}\n"
        f"تاریخ: {order['created_at']}\n\n"
        f"تعداد اقلام:\n"
    )
    for item in items:

        subtotal = item["price"] * item["quantity"]

        text += (
            f"\n"
            f"محصول: {item['name']}\n"
            f"کد: {item['product_code']}\n"
            f"تعداد: {item['quantity']}\n"
            f"قیمت: {item['price']}\n"
            f"جمع جزء: {subtotal}\n"
        )

    text += (
        f"\n"
        f"مجموع: {order['total_price']}"
    )

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "خرید مجدد",
            callback_data=f"buy_again_{order_id}"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "سفارش‌های من",
            callback_data="my_orders"
        )
    )

    bot.send_message(
        call.message.chat.id,
        text,
        reply_markup=keyboard
    )
@bot.callback_query_handler(
    func=lambda call: call.data.startswith("buy_again_")
)
def buy_again(call):

    if anti_spam_callback(call):
        return

    order_id = int(call.data.split("_")[2])

    user = get_user_by_telegram_id(call.from_user.id)

    if user is None:
        bot.answer_callback_query(
            call.id,
            "❌ کاربر پیدا نشد."
        )
        return

    items = get_order_items(order_id)

    if not items:

        bot.answer_callback_query(
            call.id,
            "❌ این سفارش محصولی ندارد."
        )
        return

    for item in items:

        add_to_cart(
            user["id"],
            item["product_id"],
            item["quantity"]
        )

    bot.answer_callback_query(
        call.id,
        "✅ محصولات به سبد خرید اضافه شدند."
    )

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "مشاهده سبد خرید",
            callback_data="view_cart"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "ادامه خرید",
            callback_data="back_categories"
        )
    )

    bot.send_message(
        call.message.chat.id,
        "محصولات این سفارش به سبد خرید شما اضافه شدند.",
        reply_markup=keyboard
    )
def check_credit(user_id):
    balance = get_wallet_balance(user_id)
    return balance > 0

@bot.callback_query_handler(
    func=lambda call: call.data == "increase_credit"
)
@bot.callback_query_handler(
    func=lambda call: call.data == "increase_credit"
)
def increase_credit(call):

    if anti_spam_callback(call):
        return
    print("افزایش اعتبار انتخاب شد")
    bot.answer_callback_query(call.id)

    msg = bot.send_message(
        call.message.chat.id,
        "💳 مبلغ اعتباری که می‌خواهید اضافه کنید را وارد کنید:"
    )

    print("در انتظار دریافت مبلغ اعتبار")
    bot.register_next_step_handler_by_chat_id(
        call.message.chat.id,
        process_credit
    )
def process_credit(message):

    if anti_spam_message(message):
        return
    print(" PROCESS CREDIT STARTED ")
    print("شناسه تلگرام کاربر:", message.from_user.id)
    print("INPUT:", message.text)
    try:
        amount = float(message.text)

        if amount <= 0:
            bot.send_message(
                message.chat.id,
                "❌ لطفاً یک مبلغ اعتبار معتبر وارد کنید."
            )
            return

        telegram_id = message.from_user.id

        user = get_user_by_telegram_id(telegram_id)

        if user is None:
            bot.send_message(
                message.chat.id,
                "❌ کاربر پیدا نشد."
            )
            return

        user_id = user["id"]

        print("شناسه کاربر در پایگاه داده:", user_id)

        add_credit(user_id, amount)

        balance = get_wallet_balance(user_id)

        print("اعتبار اضافه شد:", amount)
        print("موجودی فعلی:", balance)

        bot.send_message(
            message.chat.id,
            f"Credit added successfully.\n\n"
            f"Added: {amount:.2f}\n"
            f"اعتبار فعلی: {balance:.2f}"
        )
    except ValueError:

        bot.send_message(
            message.chat.id,
            "❌ لطفاً یک عدد معتبر وارد کنید."
        )

    except Exception as e:

        print("خطا:", e)

        bot.send_message(
            message.chat.id,
            f"An error occurred: {e}"
        )
@bot.callback_query_handler(
    func=lambda call: call.data == "my_credit"
)
def show_my_credit(call):

    if anti_spam_callback(call):
        return

    print("اعتبار من انتخاب شد")

    bot.answer_callback_query(call.id)

    telegram_id = call.from_user.id

    user = get_user_by_telegram_id(telegram_id)

    if user is None:
        bot.send_message(
            call.message.chat.id,
            "❌ کاربر پیدا نشد."
        )
        return

    user_id = user["id"]
    balance = get_wallet_balance(user_id)

    print("شناسه کاربر:", user_id)
    print("موجودی فعلی:", balance)

    bot.send_message(
        call.message.chat.id,
        f"💳 اعتبار فعلی شما:\n\n"
        f"موجودی: {balance:.2f}"
    )

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("buy_")
)
def buy_product(call):

    if anti_spam_callback(call):
        return

    print(" BUY CLICKED ")
    bot.answer_callback_query(call.id)
    product_id = int(call.data.split("_")[1])
    print("شناسه محصول:", product_id)

    product = get_product_by_id(product_id)

    if product is None:
        bot.send_message(
            call.message.chat.id,
            "❌ محصول پیدا نشد."
        )
        return

    product_name = product["name"]
    price = float(product["price"])
    stock = int(product["stock"])

    print("محصول:", product_name)
    print("قیمت:", price)
    print("موجودی:", stock)

    if stock <= 0:
        bot.send_message(
            call.message.chat.id,
            "❌ این محصول ناموجود است."
        )
        return

    telegram_id = call.from_user.id

    user = get_user_by_telegram_id(telegram_id)

    if user is None:
        bot.send_message(
            call.message.chat.id,
            "❌ کاربر پیدا نشد."
        )
        return

    user_id = user["id"]

    # Get credit
    balance = float(get_wallet_balance(user_id))

    print("شناسه کاربر:", user_id)
    print("اعتبار فعلی:", balance)

    if balance < price:

        bot.send_message(
            call.message.chat.id,
            f"❌ اعتبار کافی نیست.\n\n"
            f"اعتبار شما: {balance:.2f}\n"
            f"قیمت محصول: {price:.2f}"
        )

        return
    
    bot.send_message(
    call.message.chat.id,
    f"📦 محصول: {product_name}\n"
    f"💰 قیمت: {price:.2f}\n"
    f"💳 اعتبار شما: {balance:.2f}\n"
    f"📊 موجودی: {stock}\n\n"
    f"آیا از خرید این محصول اطمینان دارید؟",
    reply_markup=purchase_confirmation_keyboard(product_id))

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("confirm_buy_")
)
def confirm_purchase(call):

    if anti_spam_callback(call):
        return
    print(" CONFIRM PURCHASE ")
    bot.answer_callback_query(call.id)
    try:

        product_id = int(call.data.split("_")[2])

        print("شناسه محصول:", product_id)

        product = get_product_by_id(product_id)

        if product is None:

            bot.send_message(
                call.message.chat.id,
                "❌ محصول پیدا نشد."
            )

            return

        product_name = product["name"]
        price = float(product["price"])
        stock = int(product["stock"])

        print("محصول:", product_name)
        print("قیمت:", price)
        print("موجودی:", stock)

        # Check stock again
        if stock <= 0:

            bot.send_message(
                call.message.chat.id,
                "❌ متأسفانه این محصول موجود نیست."
            )

            return

        telegram_id = call.from_user.id
        user = get_user_by_telegram_id(telegram_id)

        if user is None:

            bot.send_message(
                call.message.chat.id,
                "❌ کاربر پیدا نشد."
            )

            return

        user_id = user["id"]

        # Get current credit
        balance = float(
            get_wallet_balance(user_id)
        )
        print("شناسه کاربر:", user_id)
        print("اعتبار فعلی:", balance)

        if balance < price:

            bot.send_message(
                call.message.chat.id,
                f"❌ اعتبار کافی نیست.\n\n"
                f"اعتبار شما: {balance:.2f}\n"
                f"قیمت محصول: {price:.2f}"
            )

            return
        # Deduct credit
        credit_updated = deduct_credit(
            user_id,
            price
        )
        if not credit_updated:

            bot.send_message(
                call.message.chat.id,
                "❌ کسر اعتبار انجام نشد."
            )

            return

        print("اعتبار کسر شد")

        # Create an order for the direct purchase
        order_number = f"ORD-{int(time.time())}"

        order_id = insert_order(
            order_number,
            user_id,
            "completed",
            price,
            user.get("address") or "",
            "خرید مستقیم از تلگرام"
        )

        insert_order_item(
            order_id,
            product_id,
            1,
            price
        )
        # Decrease stock
        stock_updated = decrease_stock(
            product_id
        )
        if not stock_updated:

            bot.send_message(
                call.message.chat.id,
                "❌ به‌روزرسانی موجودی محصول انجام نشد."
            )

            return
        print("موجودی کاهش یافت")

        new_balance = get_wallet_balance(user_id)

        bot.send_message(
            call.message.chat.id,
            f"خرید با موفقیت انجام شد. ✅\n\n"
            f"محصول: {product_name}\n"
            f"قیمت: {price:,.2f}\n"
            f"شماره سفارش: {order_number}\n\n"
            f"✅ سفارش شما با موفقیت ثبت شد.",
            reply_markup=main_menu()
        )

        print(" PURCHASE COMPLETED ")

    except Exception as e:

        print("خطای خرید:", e)

        bot.send_message(
            call.message.chat.id,
            f"❌ خطایی رخ داد:\n{e}"
        )
        
def cancel_purchase(call):

    if anti_spam_callback(call):
        return

    print("خرید لغو شد")

    bot.answer_callback_query(call.id)

    bot.send_message(
        call.message.chat.id,
        "❌ خرید لغو شد."
    )
# ADMIN PANEL

def admin_panel_keyboard():
    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "👤 کاربران",
            callback_data="admin_users"
        ),
        types.InlineKeyboardButton(
            "📦 محصولات",
            callback_data="admin_products"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "🧾 سفارش‌ها",
            callback_data="admin_orders"
        )
    )
    keyboard.add(
        types.InlineKeyboardButton(
            "🏠 خانه",
            callback_data="admin_home"
        )
    )
    return keyboard

def is_admin(cid):
    return cid == ADMIN_ID


def get_admin_stats():
    stats = {
        "users": 0,
        "products": 0,
        "orders": 0,
    }
    try:
        stats["users"] = len(get_users())
    except Exception as error:
        print("خطا در دریافت کاربران ادمین:", error)
    try:
        stats["products"] = len(get_products())
    except Exception as error:
        print("خطا در دریافت محصولات ادمین:", error)
    try:
        stats["orders"] = len(get_orders())
    except Exception as error:
        print("خطا در دریافت سفارش‌های ادمین:", error)
    return stats

@bot.message_handler(commands=["admin"])
def admin_command(message):

    if anti_spam_message(message):
        return
    cid = message.from_user.id
    if not is_admin(cid):
        bot.send_message(
            message.chat.id,
            "⛔ دسترسی به پنل مدیریت ندارید.",
            reply_markup=main_menu()
        )
        return

    stats = get_admin_stats()

    text = (
        "🔐 پنل مدیریت PRN-Shop\n\n"
        f"👤 تعداد کاربران: {stats['users']}\n"
        f"📦 تعداد محصولات: {stats['products']}\n"
        f"🧾 تعداد سفارش‌ها: {stats['orders']}\n\n"
        "یکی از گزینه‌های زیر را انتخاب کنید:"
    )

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=admin_panel_keyboard()
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_"))
def admin_callback(call):

    if anti_spam_callback(call):
        return
    cid = call.from_user.id

    if not is_admin(cid):
        bot.answer_callback_query(
            call.id,
            "⛔ دسترسی مجاز نیست."
        )
        return
    action = call.data
    if action == "admin_home":

        bot.answer_callback_query(call.id)

        bot.send_message(
            cid,
            "🏠 منوی اصلی PRN-Shop",
            reply_markup=main_menu()
        )

        return
    if action == "admin_users":

        try:
            users = get_users()

            bot.answer_callback_query(
                call.id,
                f"تعداد کاربران: {len(users)}"
            )

            bot.send_message(
                cid,
                f"👤 تعداد کاربران: {len(users)}"
            )
        except Exception as error:

            bot.answer_callback_query(call.id)

            bot.send_message(
                cid,
                f"خطا در دریافت کاربران:\n{error}"
            )

        return
    if action == "admin_products":

        try:
            products_list = get_products()

            bot.answer_callback_query(
                call.id,
                f"تعداد محصولات: {len(products_list)}"
            )

            bot.send_message(
                cid,
                f"📦 تعداد محصولات: {len(products_list)}"
            )
        except Exception as error:

            bot.answer_callback_query(call.id)
            bot.send_message(
                cid,
                f"خطا در دریافت محصولات:\n{error}"
            )

        return
    if action == "admin_orders":

        try:
            orders_list = get_orders()
            bot.answer_callback_query(
                call.id,
                f"تعداد سفارش‌ها: {len(orders_list)}"
            )
            bot.send_message(
                cid,
                f"🧾 تعداد سفارش‌ها: {len(orders_list)}"
            )
        except Exception as error:

            bot.answer_callback_query(call.id)

            bot.send_message(
                cid,
                f"خطا در دریافت سفارش‌ها:\n{error}"
            )
#Bot commands 

@bot.message_handler(commands=["menu"])
def menu_command(message):

    if anti_spam_message(message):
        return

    bot.send_message(
        message.chat.id,
        "🏠 منوی اصلی PRN-Shop",
        reply_markup=main_menu()
    )
@bot.message_handler(commands=["catalog"])
def catalog_command(message):

    if anti_spam_message(message):
        return

    catalog_menu_handler(message)

@bot.message_handler(commands=["contact"])
def contact_command(message):

    if anti_spam_message(message):
        return

    bot.send_message(
        message.chat.id,
        "☎️ تماس با ما\n\n"
        "برای ارتباط با پشتیبانی، پیام خود را همین‌جا ارسال کنید."
    )

@bot.message_handler(commands=["help"])
def help_command(message):

    if anti_spam_message(message):
        return

    text = (
        "ℹ️ راهنمای PRN-Shop\n\n"
        "/start - شروع ربات\n"
        "/help - نمایش راهنما\n"
        "/menu - منوی اصلی\n"
        "/catalog - کاتالوگ\n"
        "/contact - تماس با ما"
    )

    if is_admin(message.from_user.id):
        text += "\n/admin - پنل مدیریت"

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=main_menu()
    )

print("Finally started!")

bot.infinity_polling()
