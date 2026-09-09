from config import get_connection
import uuid


def register_user(message):
    user = message.from_user
    conn = get_connection()
    cur = conn.cursor()
    try:
        sql = """
        INSERT INTO users
        (telegram_id, first_name, last_name, username, phone, address)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cur.execute(sql, (
            user.id, user.first_name, user.last_name,
            user.username, None, None
        ))
        conn.commit()
    finally:
        cur.close()
        conn.close()


def insert_category(title, parent_id=None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO categories(title, parent_id) VALUES (%s, %s)",
            (title, parent_id)
        )
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close()
        conn.close()


def insert_product(product_code, category_id, name, description,
                   price, stock, minimum_stock=0):
    # minimum_stock is kept in the Python signature for compatibility,
    # but the live products table does not contain that column.
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO products
            (product_code, category_id, name, description, price, stock)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (product_code, category_id, name, description, price, stock)
        )
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close()
        conn.close()


def insert_user(telegram_id, first_name, last_name, username, phone, address):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO users
            (telegram_id, first_name, last_name, username, phone, address)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (telegram_id, first_name, last_name, username, phone, address)
        )
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close()
        conn.close()


def insert_order(order_number, user_id, status, total_price, address, description):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO orders
            (order_number, user_id, status, total_price, address, description)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (order_number, user_id, status, total_price, address, description)
        )
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close()
        conn.close()


def insert_order_item(order_id, product_id, quantity, price):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO order_items
            (order_id, product_id, quantity, unit_price)
            VALUES (%s, %s, %s, %s)
            """,
            (order_id, product_id, quantity, price)
        )
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close()
        conn.close()


def insert_cart(user_id, product_id, quantity=1):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO carts (user_id, product_id, quantity)
            VALUES (%s, %s, %s)
            """,
            (user_id, product_id, quantity)
        )
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close()
        conn.close()


def add_to_cart(user_id, product_id, quantity=1):
    if quantity < 1:
        quantity = 1

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            SELECT id, quantity
            FROM carts
            WHERE user_id = %s AND product_id = %s
            """,
            (user_id, product_id)
        )
        existing = cur.fetchone()

        if existing:
            cur.execute(
                "UPDATE carts SET quantity = quantity + %s WHERE id = %s",
                (quantity, existing[0])
            )
        else:
            cur.execute(
                """
                INSERT INTO carts (user_id, product_id, quantity)
                VALUES (%s, %s, %s)
                """,
                (user_id, product_id, quantity)
            )

        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def insert_stock_notification(user_id, product_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO stock_notifications (user_id, product_id)
            VALUES (%s, %s)
            """,
            (user_id, product_id)
        )
        conn.commit()
        return True
    finally:
        cur.close()
        conn.close()


def update_cart_quantity(cart_id, quantity):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE carts SET quantity = %s WHERE id = %s",
            (quantity, cart_id)
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        cur.close()
        conn.close()


def remove_from_cart(cart_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM carts WHERE id = %s", (cart_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        cur.close()
        conn.close()


def decrease_product_stock(product_id, quantity):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE products
            SET stock = stock - %s
            WHERE id = %s AND stock >= %s
            """,
            (quantity, product_id, quantity)
        )
        conn.commit()
        return cur.rowcount
    finally:
        cur.close()
        conn.close()


def add_existing_product_to_cart(user_id, product_id, quantity):
    return add_to_cart(user_id, product_id, quantity)


def create_wallet(user_id):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO wallet (user_id, balance)
            VALUES (%s, 0)
            ON DUPLICATE KEY UPDATE user_id = user_id
            """,
            (user_id,)
        )
        conn.commit()
        return True
    finally:
        cur.close()
        conn.close()


def increase_wallet_balance(user_id, amount):
    return add_credit(user_id, amount)


def add_credit(user_id, amount):
    if amount <= 0:
        return False

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO wallet (user_id, balance)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE balance = balance + %s
            """,
            (user_id, amount, amount)
        )
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def deduct_credit(user_id, amount):
    if amount <= 0:
        return False

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE wallet
            SET balance = balance - %s
            WHERE user_id = %s AND balance >= %s
            """,
            (amount, user_id, amount)
        )
        conn.commit()
        return cur.rowcount > 0
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def decrease_stock(product_id):
    return decrease_product_stock(product_id, 1) > 0


def _new_order_number():
    return "ORD-" + uuid.uuid4().hex[:12].upper()


def purchase_product(user_id, product_id, address="", description="خرید مستقیم از تلگرام"):
    """
    Atomic direct purchase.
    Order creation, order item, stock decrement and wallet deduction
    all happen in ONE transaction. If anything fails, everything rolls back.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    try:
        cur.execute(
            """
            SELECT id, name, product_code, price, stock
            FROM products
            WHERE id = %s
            FOR UPDATE
            """,
            (product_id,)
        )
        product = cur.fetchone()

        if product is None:
            raise ValueError("محصول پیدا نشد.")

        if int(product["stock"]) < 1:
            raise ValueError("این محصول موجود نیست.")

        cur.execute(
            """
            SELECT user_id, balance
            FROM wallet
            WHERE user_id = %s
            FOR UPDATE
            """,
            (user_id,)
        )
        wallet = cur.fetchone()

        if wallet is None:
            raise ValueError("کیف پول کاربر پیدا نشد.")

        price = product["price"]
        if wallet["balance"] < price:
            raise ValueError("اعتبار کافی نیست.")

        order_number = _new_order_number()

        cur.execute(
            """
            INSERT INTO orders
            (order_number, user_id, status, total_price, address, description)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                order_number, user_id, "completed",
                price, address or "", description
            )
        )
        order_id = cur.lastrowid

        cur.execute(
            """
            INSERT INTO order_items
            (order_id, product_id, quantity, unit_price)
            VALUES (%s, %s, %s, %s)
            """,
            (order_id, product_id, 1, price)
        )

        cur.execute(
            """
            UPDATE products
            SET stock = stock - 1
            WHERE id = %s AND stock >= 1
            """,
            (product_id,)
        )
        if cur.rowcount != 1:
            raise ValueError("موجودی محصول تغییر کرده است. دوباره تلاش کنید.")

        cur.execute(
            """
            UPDATE wallet
            SET balance = balance - %s
            WHERE user_id = %s AND balance >= %s
            """,
            (price, user_id, price)
        )
        if cur.rowcount != 1:
            raise ValueError("اعتبار کافی نیست.")

        conn.commit()

        return {
            "order_id": order_id,
            "order_number": order_number,
            "product_name": product["name"],
            "product_code": product["product_code"],
            "price": price,
            "new_stock": int(product["stock"]) - 1,
            "new_balance": wallet["balance"] - price,
        }

    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def checkout_cart_transaction(user_id, address="", description="خرید از سبد خرید"):
    """
    Atomic cart checkout. Locks the products and wallet, validates all items,
    creates the order, inserts order items, decreases stock, deducts credit,
    clears the cart, then commits.
    """
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    try:
        cur.execute(
            """
            SELECT
                c.id AS cart_id,
                c.product_id,
                c.quantity,
                p.name,
                p.product_code,
                p.price,
                p.stock
            FROM carts c
            INNER JOIN products p ON c.product_id = p.id
            WHERE c.user_id = %s
            ORDER BY c.id
            FOR UPDATE
            """,
            (user_id,)
        )
        items = cur.fetchall()

        if not items:
            raise ValueError("سبد خرید شما خالی است.")

        total = 0
        for item in items:
            qty = int(item["quantity"])
            stock = int(item["stock"])
            if qty < 1:
                raise ValueError("تعداد یکی از محصولات نامعتبر است.")
            if stock < qty:
                raise ValueError(
                    f"موجودی «{item['name']}» کافی نیست. موجودی: {stock}"
                )
            total += item["price"] * qty

        cur.execute(
            """
            SELECT user_id, balance
            FROM wallet
            WHERE user_id = %s
            FOR UPDATE
            """,
            (user_id,)
        )
        wallet = cur.fetchone()

        if wallet is None:
            raise ValueError("کیف پول کاربر پیدا نشد.")

        if wallet["balance"] < total:
            raise ValueError(
                f"اعتبار کافی نیست. اعتبار شما: {wallet['balance']:.2f} | "
                f"مبلغ سفارش: {total:.2f}"
            )

        order_number = _new_order_number()

        cur.execute(
            """
            INSERT INTO orders
            (order_number, user_id, status, total_price, address, description)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                order_number, user_id, "completed",
                total, address or "", description
            )
        )
        order_id = cur.lastrowid

        for item in items:
            qty = int(item["quantity"])

            cur.execute(
                """
                INSERT INTO order_items
                (order_id, product_id, quantity, unit_price)
                VALUES (%s, %s, %s, %s)
                """,
                (order_id, item["product_id"], qty, item["price"])
            )

            cur.execute(
                """
                UPDATE products
                SET stock = stock - %s
                WHERE id = %s AND stock >= %s
                """,
                (qty, item["product_id"], qty)
            )
            if cur.rowcount != 1:
                raise ValueError(
                    f"موجودی «{item['name']}» در لحظه خرید کافی نبود."
                )

        cur.execute(
            """
            UPDATE wallet
            SET balance = balance - %s
            WHERE user_id = %s AND balance >= %s
            """,
            (total, user_id, total)
        )
        if cur.rowcount != 1:
            raise ValueError("اعتبار کافی نیست.")

        cur.execute("DELETE FROM carts WHERE user_id = %s", (user_id,))

        conn.commit()

        return {
            "order_id": order_id,
            "order_number": order_number,
            "total": total,
            "new_balance": wallet["balance"] - total,
            "items": items,
        }

    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
