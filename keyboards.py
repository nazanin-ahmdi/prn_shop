from telebot.types import ReplyKeyboardMarkup
from telebot.types import KeyboardButton
from telebot.types import InlineKeyboardMarkup
from telebot.types import InlineKeyboardButton
from telebot import types


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
        KeyboardButton("🌐 Language")
    )

    return keyboard

def product_inline_keyboard(product_id):

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "Buy",
            callback_data=f"buy_{product_id}"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "Add To Cart",
            callback_data=f"add_{product_id}"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "Back",
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
            "Remove",
            callback_data=f"cart_remove_{cart_id}"
        )
    )

    return keyboard

def cart_checkout_keyboard():

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "Checkout",
            callback_data="checkout"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "Continue Shopping",
            callback_data="back_categories"
        )
    )

    return keyboard
def orders_keyboard():

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "My Orders",
            callback_data="my_orders"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "Continue Shopping",
            callback_data="back_categories"
        )
    )

    return keyboard

def credit_keyboard():

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "Increase Credit",
            callback_data="increase_credit"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "My Credit",
            callback_data="my_credit"
        )
    )

    return keyboard

def purchase_confirmation_keyboard(product_id):

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "Confirm Purchase",
            callback_data=f"confirm_buy_{product_id}"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "Cancel",
            callback_data="cancel_buy"
        )
    )

    return keyboard