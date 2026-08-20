from main import bot
from keyboards import product_inline_keyboard
print('handler bot:',id(bot))

from DQL import *
from DML import *
from telebot import types
from texts import *
import time

from keyboards import *

from texts import WELCOME


@bot.message_handler(commands=["start"])
def start(message):

    print("START COMMAND")

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
@bot.message_handler(func=lambda message: message.text == "💳 اعتبار من")
def my_credit(message):

    user = get_user_by_telegram_id(
        message.from_user.id
    )

    if user is None:
        bot.send_message(
            message.chat.id,
            "User not found."
        )
        return

    balance = get_wallet_balance(user["id"])

    bot.send_message(
        message.chat.id,
        f"Your Credit: {balance:,.2f}",
        reply_markup=credit_keyboard()
    )

@bot.message_handler(func=lambda message: message.text == "🛍 محصولات")
def products(message):

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

    product = get_product_by_name(message.text)

   


    text = f"""
📦 Name : {product['name']}

🔖 Code : {product['product_code']}

💰 Price : {product['price']}

📦 Stock : {product['stock']}

📝 Description :

{product['description']}
"""

    bot.send_message(
    message.chat.id,
    text,
    reply_markup=product_inline_keyboard(product["id"])
    )
@bot.callback_query_handler(func=lambda call: call.data.startswith("add_"))
def add_product_to_cart(call):

    product_id = int(call.data.split("_")[1])

    user = get_user_by_telegram_id(call.from_user.id)

    if user is None:
        bot.answer_callback_query(
            call.id,
            "User not found."
        )
        return

    add_to_cart(
        user["id"],
        product_id
    )

    bot.answer_callback_query(
        call.id,
        "Product added to cart."
    )

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "View Cart",
            callback_data="view_cart"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "Continue Shopping",
            callback_data="back_categories"
        )
    )

    bot.send_message(
        call.message.chat.id,
        "Product added to cart.",
        reply_markup=keyboard
    )
@bot.callback_query_handler(func=lambda call: call.data == "view_cart")
def view_cart(call):

    user = get_user_by_telegram_id(call.from_user.id)

    if user is None:
        bot.answer_callback_query(
            call.id,
            "User not found."
        )
        return

    items = get_cart_items(user["id"])

    bot.answer_callback_query(call.id)

    if not items:

        bot.send_message(
            call.message.chat.id,
            "🛒 Your cart is empty."
        )

        return

    bot.send_message(
        call.message.chat.id,
        "🛒 Your Cart"
    )

    total = 0

    for item in items:

        subtotal = item["price"] * item["quantity"]

        total += subtotal

        text = (
            f"📦 {item['name']}\n"
            f"Code: {item['product_code']}\n"
            f"Price: {item['price']}\n"
            f"Quantity: {item['quantity']}\n"
            f"Subtotal: {subtotal}"
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
        f"💰 Total: {total}",
        reply_markup=cart_checkout_keyboard()
    )
def refresh_cart_item(call, cart_id):

    item = get_cart_item(cart_id)

    if item is None:
        return

    subtotal = item["price"] * item["quantity"]

    text = (
        f"Product: {item['name']}\n"
        f"Code: {item['product_code']}\n"
        f"Price: {item['price']}\n"
        f"Quantity: {item['quantity']}\n"
        f"Subtotal: {subtotal}"
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

    cart_id = int(call.data.split("_")[2])

    item = get_cart_item(cart_id)

    if item is None:
        bot.answer_callback_query(
            call.id,
            "Cart item not found."
        )
        return

    new_quantity = item["quantity"] + 1

    if new_quantity > item["stock"]:
        bot.answer_callback_query(
            call.id,
            "Not enough stock."
        )
        return

    update_cart_quantity(
        cart_id,
        new_quantity
    )

    bot.answer_callback_query(
        call.id,
        "Quantity increased."
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
            "Cart item not found."
        )
        return

    new_quantity = item["quantity"] - 1

    if new_quantity <= 0:
        remove_from_cart(cart_id)

        bot.answer_callback_query(
            call.id,
            "Product removed from cart."
        )

        bot.edit_message_text(
            "Product removed from cart.",
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
        "Quantity decreased."
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
            "Cart item not found."
        )
        return

    new_quantity = item["quantity"] - 1

    if new_quantity <= 0:
        remove_from_cart(cart_id)

        bot.answer_callback_query(
            call.id,
            "Product removed from cart."
        )

        bot.edit_message_text(
            "Product removed from cart.",
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
        "Quantity decreased."
    )

    refresh_cart_item(call, cart_id)

@bot.callback_query_handler(
    func=lambda call: call.data == "checkout"
)
def checkout(call):

    user = get_user_by_telegram_id(call.from_user.id)

    if user is None:
        bot.answer_callback_query(
            call.id,
            "User not found."
        )
        return

    items = get_cart_items(user["id"])

    if not items:
        bot.answer_callback_query(
            call.id,
            "Your cart is empty."
        )
        return

    total = 0

    for item in items:
        total += item["price"] * item["quantity"]

    bot.answer_callback_query(call.id)

    text = (
        "Order Confirmation\n\n"
        f"Items: {len(items)}\n"
        f"Total: {total}\n\n"
        "Do you want to place this order?"
    )

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "Confirm Order",
            callback_data="confirm_order"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "Cancel",
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

    user = get_user_by_telegram_id(call.from_user.id)

    if user is None:
        bot.answer_callback_query(
            call.id,
            "User not found."
        )
        return

    user_id = user["id"]

    # Get current cart
    items = get_cart_items(user_id)

    if not items:

        bot.answer_callback_query(
            call.id,
            "Your cart is empty."
        )

        bot.send_message(
            call.message.chat.id,
            "Your cart is empty."
        )

        return

    # Calculate total
    total = 0

    for item in items:
        total += item["price"] * item["quantity"]

    # Check stock before creating order
    for item in items:

        if item["quantity"] > item["stock"]:

            bot.answer_callback_query(
                call.id,
                "Not enough stock."
            )

            bot.send_message(
                call.message.chat.id,
                f"Not enough stock for {item['name']}."
            )

            return

    # Create order number
    order_number = f"ORD-{int(time.time())}"

    # Create order
    order_id = insert_order(
        order_number,
        user_id,
        "pending",
        total,
        "",
        "Telegram order"
    )

    # Create order items
    for item in items:

        insert_order_item(
            order_id,
            item["product_id"],
            item["quantity"],
            item["price"]
        )

        # Decrease stock
        decrease_product_stock(
            item["product_id"],
            item["quantity"]
        )

        # Remove item from cart
        remove_from_cart(
            item["cart_id"]
        )

    bot.answer_callback_query(
        call.id,
        "Order confirmed."
    )

    bot.send_message(
        call.message.chat.id,
        f"""
Order successfully placed.

Order Number: {order_number}

Total: {total}

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

    user = get_user_by_telegram_id(call.from_user.id)

    if user is None:
        bot.answer_callback_query(
            call.id,
            "User not found."
        )
        return

    orders = get_orders_by_user(user["id"])

    bot.answer_callback_query(call.id)

    if not orders:

        bot.send_message(
            call.message.chat.id,
            "You don't have any orders yet."
        )

        return

    bot.send_message(
        call.message.chat.id,
        "My Orders"
    )

    for order in orders:

        text = (
            f"Order Number: {order['order_number']}\n"
            f"Status: {order['status']}\n"
            f"Total: {order['total_price']}\n"
            f"Date: {order['created_at']}"
        )

        keyboard = types.InlineKeyboardMarkup()

        keyboard.add(
            types.InlineKeyboardButton(
                "View Order",
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

    order_id = int(call.data.split("_")[1])

    user = get_user_by_telegram_id(call.from_user.id)

    if user is None:
        bot.answer_callback_query(
            call.id,
            "User not found."
        )
        return

    # Get order
    orders = get_orders_by_user(user["id"])

    order = None

    for item in orders:
        if item["id"] == order_id:
            order = item
            break

    if order is None:

        bot.answer_callback_query(
            call.id,
            "Order not found."
        )
        return

    # Get order items
    items = get_order_items(order_id)

    bot.answer_callback_query(call.id)

    text = (
        f"Order Details\n\n"
        f"Order Number: {order['order_number']}\n"
        f"Status: {order['status']}\n"
        f"Date: {order['created_at']}\n\n"
        f"Items:\n"
    )

    for item in items:

        subtotal = item["price"] * item["quantity"]

        text += (
            f"\n"
            f"Product: {item['name']}\n"
            f"Code: {item['product_code']}\n"
            f"Quantity: {item['quantity']}\n"
            f"Price: {item['price']}\n"
            f"Subtotal: {subtotal}\n"
        )

    text += (
        f"\n"
        f"Total: {order['total_price']}"
    )

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "Buy Again",
            callback_data=f"buy_again_{order_id}"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "My Orders",
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

    order_id = int(call.data.split("_")[2])

    user = get_user_by_telegram_id(call.from_user.id)

    if user is None:
        bot.answer_callback_query(
            call.id,
            "User not found."
        )
        return

    items = get_order_items(order_id)

    if not items:

        bot.answer_callback_query(
            call.id,
            "Order has no products."
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
        "Products added to cart."
    )

    keyboard = types.InlineKeyboardMarkup()

    keyboard.add(
        types.InlineKeyboardButton(
            "View Cart",
            callback_data="view_cart"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "Continue Shopping",
            callback_data="back_categories"
        )
    )

    bot.send_message(
        call.message.chat.id,
        "The products from this order have been added to your cart.",
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

    print("INCREASE CREDIT CLICKED")

    bot.answer_callback_query(call.id)

    msg = bot.send_message(
        call.message.chat.id,
        "Please enter the amount of credit you want to add:"
    )

    print("WAITING FOR CREDIT")

    bot.register_next_step_handler_by_chat_id(
        call.message.chat.id,
        process_credit
    )


def process_credit(message):

    print("========== PROCESS CREDIT STARTED ==========")
    print("USER TELEGRAM ID:", message.from_user.id)
    print("INPUT:", message.text)

    try:
        amount = float(message.text)

        if amount <= 0:
            bot.send_message(
                message.chat.id,
                "Please enter a valid credit amount."
            )
            return

        telegram_id = message.from_user.id

        user = get_user_by_telegram_id(telegram_id)

        if user is None:
            bot.send_message(
                message.chat.id,
                "User not found."
            )
            return

        user_id = user["id"]

        print("DATABASE USER ID:", user_id)

        add_credit(user_id, amount)

        balance = get_wallet_balance(user_id)

        print("CREDIT ADDED:", amount)
        print("CURRENT BALANCE:", balance)

        bot.send_message(
            message.chat.id,
            f"Credit added successfully.\n\n"
            f"Added: {amount:.2f}\n"
            f"Current Credit: {balance:.2f}"
        )

    except ValueError:

        bot.send_message(
            message.chat.id,
            "Please enter a valid number."
        )

    except Exception as e:

        print("ERROR:", e)

        bot.send_message(
            message.chat.id,
            f"An error occurred: {e}"
        )
@bot.callback_query_handler(
    func=lambda call: call.data == "my_credit"
)
def show_my_credit(call):

    print("MY CREDIT CLICKED")

    bot.answer_callback_query(call.id)

    telegram_id = call.from_user.id

    user = get_user_by_telegram_id(telegram_id)

    if user is None:
        bot.send_message(
            call.message.chat.id,
            "User not found."
        )
        return

    user_id = user["id"]

    balance = get_wallet_balance(user_id)

    print("USER ID:", user_id)
    print("CURRENT BALANCE:", balance)

    bot.send_message(
        call.message.chat.id,
        f"Your Current Credit:\n\n"
        f"Balance: {balance:.2f}"
    )

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("buy_")
)
def buy_product(call):

    print("========== BUY CLICKED ==========")

    bot.answer_callback_query(call.id)

    product_id = int(call.data.split("_")[1])

    print("PRODUCT ID:", product_id)

    # Get product
    product = get_product_by_id(product_id)

    if product is None:
        bot.send_message(
            call.message.chat.id,
            "Product not found."
        )
        return

    product_name = product["name"]
    price = float(product["price"])
    stock = int(product["stock"])

    print("PRODUCT:", product_name)
    print("PRICE:", price)
    print("STOCK:", stock)

    # Check stock
    if stock <= 0:
        bot.send_message(
            call.message.chat.id,
            "This product is out of stock."
        )
        return

    # Get user
    telegram_id = call.from_user.id

    user = get_user_by_telegram_id(telegram_id)

    if user is None:
        bot.send_message(
            call.message.chat.id,
            "User not found."
        )
        return

    user_id = user["id"]

    # Get credit
    balance = float(get_wallet_balance(user_id))

    print("USER ID:", user_id)
    print("CURRENT CREDIT:", balance)

    # Check credit
    if balance < price:

        bot.send_message(
            call.message.chat.id,
            f"Insufficient credit.\n\n"
            f"Your Credit: {balance:.2f}\n"
            f"Product Price: {price:.2f}"
        )

        return

    # Credit is enough
    bot.send_message(
    call.message.chat.id,
    f"Product: {product_name}\n"
    f"Price: {price:.2f}\n"
    f"Your Credit: {balance:.2f}\n"
    f"Stock: {stock}\n\n"
    f"Are you sure you want to purchase this product?",
    reply_markup=purchase_confirmation_keyboard(product_id)
)
@bot.callback_query_handler(
    func=lambda call: call.data.startswith("confirm_buy_")
)
@bot.callback_query_handler(
    func=lambda call: call.data.startswith("confirm_buy_")
)
def confirm_purchase(call):

    print("========== CONFIRM PURCHASE ==========")

    bot.answer_callback_query(call.id)

    try:

        product_id = int(call.data.split("_")[2])

        print("PRODUCT ID:", product_id)

        # Get product again
        product = get_product_by_id(product_id)

        if product is None:

            bot.send_message(
                call.message.chat.id,
                "Product not found."
            )

            return

        product_name = product["name"]
        price = float(product["price"])
        stock = int(product["stock"])

        print("PRODUCT:", product_name)
        print("PRICE:", price)
        print("STOCK:", stock)

        # Check stock again
        if stock <= 0:

            bot.send_message(
                call.message.chat.id,
                "Sorry, this product is out of stock."
            )

            return

        # Get user
        telegram_id = call.from_user.id

        user = get_user_by_telegram_id(telegram_id)

        if user is None:

            bot.send_message(
                call.message.chat.id,
                "User not found."
            )

            return

        user_id = user["id"]

        # Get current credit
        balance = float(
            get_wallet_balance(user_id)
        )

        print("USER ID:", user_id)
        print("CURRENT CREDIT:", balance)

        # Check credit again
        if balance < price:

            bot.send_message(
                call.message.chat.id,
                f"Insufficient credit.\n\n"
                f"Your Credit: {balance:.2f}\n"
                f"Product Price: {price:.2f}"
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
                "Unable to deduct credit."
            )

            return

        print("CREDIT DEDUCTED")

        # Decrease stock
        stock_updated = decrease_stock(
            product_id
        )

        if not stock_updated:

            bot.send_message(
                call.message.chat.id,
                "Unable to update product stock."
            )

            return

        print("STOCK DECREASED")

        # Get new balance
        new_balance = get_wallet_balance(user_id)

        bot.send_message(
            call.message.chat.id,
            f"Purchase successful.\n\n"
            f"Product: {product_name}\n"
            f"Price: {price:.2f}\n"
            f"Remaining Credit: {new_balance:.2f}\n"
            f"Previous Stock: {stock}\n"
            f"Remaining Stock: {stock - 1}"
        )

        print("========== PURCHASE COMPLETED ==========")

    except Exception as e:

        print("PURCHASE ERROR:", e)

        bot.send_message(
            call.message.chat.id,
            f"An error occurred:\n{e}"
        )
        
def cancel_purchase(call):

    print("PURCHASE CANCELLED")

    bot.answer_callback_query(call.id)

    bot.send_message(
        call.message.chat.id,
        "Purchase cancelled."
    )
