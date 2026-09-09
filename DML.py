from config import get_connection
from datetime import datetime


def register_user(message):
    user = message.from_user
    conn = get_connection()
    cur = conn.cursor()
    try:
        sql = """
        INSERT INTO users
        (telegram_id, first_name, last_name, username, phone, address)
        VALUES (%s,%s,%s,%s,%s,%s)
        """
        cur.execute(sql, (user.id, user.first_name, user.last_name,
                          user.username, None, None))
        conn.commit()
    finally:
        cur.close(); conn.close()


def insert_category(title, parent_id=None):
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("INSERT INTO categories(title, parent_id) VALUES (%s,%s)",
                    (title, parent_id))
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close(); conn.close()


def insert_product(product_code, category_id, name, description, price, stock,
                   minimum_stock=0):
    # Live products table does NOT contain minimum_stock, so do not insert it.
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO products
            (product_code, category_id, name, description, price, stock)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (product_code, category_id, name, description, price, stock))
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close(); conn.close()


def insert_user(telegram_id, first_name, last_name, username, phone, address):
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO users
            (telegram_id, first_name, last_name, username, phone, address)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (telegram_id, first_name, last_name, username, phone, address))
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close(); conn.close()


def insert_order(order_number, user_id, status, total_price, address, description):
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO orders
            (order_number, user_id, status, total_price, address, description)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (order_number, user_id, status, total_price, address, description))
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close(); conn.close()


def insert_order_item(order_id, product_id, quantity, price):
    conn = get_connection(); cur = conn.cursor()
    try:
        # IMPORTANT: live DB column is unit_price, not price.
        cur.execute("""
            INSERT INTO order_items
            (order_id, product_id, quantity, unit_price)
            VALUES (%s,%s,%s,%s)
        """, (order_id, product_id, quantity, price))
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close(); conn.close()


def insert_cart(user_id, product_id, quantity=1):
    return add_to_cart(user_id, product_id, quantity)


def add_to_cart(user_id, product_id, quantity=1):
    quantity = int(quantity)
    if quantity < 1:
        quantity = 1
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, quantity
            FROM carts
            WHERE user_id=%s AND product_id=%s
            FOR UPDATE
        """, (user_id, product_id))
        existing = cur.fetchone()
        if existing:
            cur.execute("UPDATE carts SET quantity=%s WHERE id=%s",
                        (int(existing[1]) + quantity, existing[0]))
        else:
            cur.execute("""
                INSERT INTO carts (user_id, product_id, quantity)
                VALUES (%s,%s,%s)
            """, (user_id, product_id, quantity))
        conn.commit()
        return True
    finally:
        cur.close(); conn.close()


def insert_stock_notification(user_id, product_id):
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("INSERT INTO stock_notifications(user_id, product_id) VALUES (%s,%s)",
                    (user_id, product_id))
        conn.commit()
    finally:
        cur.close(); conn.close()


def update_cart_quantity(cart_id, quantity):
    quantity = int(quantity)
    if quantity <= 0:
        return remove_from_cart(cart_id)
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("UPDATE carts SET quantity=%s WHERE id=%s", (quantity, cart_id))
        conn.commit()
        return cur.rowcount > 0
    finally:
        cur.close(); conn.close()


def remove_from_cart(cart_id):
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("DELETE FROM carts WHERE id=%s", (cart_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        cur.close(); conn.close()


def decrease_product_stock(product_id, quantity):
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE products
            SET stock=stock-%s
            WHERE id=%s AND stock >= %s
        """, (quantity, product_id, quantity))
        conn.commit()
        return cur.rowcount
    finally:
        cur.close(); conn.close()


def add_existing_product_to_cart(user_id, product_id, quantity):
    return add_to_cart(user_id, product_id, quantity)


def create_wallet(user_id):
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("INSERT INTO wallet(user_id,balance) VALUES (%s,0)", (user_id,))
        conn.commit()
    finally:
        cur.close(); conn.close()


def increase_wallet_balance(user_id, amount):
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("UPDATE wallet SET balance=balance+%s WHERE user_id=%s",
                    (amount, user_id))
        conn.commit()
        return cur.rowcount > 0
    finally:
        cur.close(); conn.close()


def add_credit(user_id, amount):
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO wallet(user_id,balance) VALUES (%s,%s)
            ON DUPLICATE KEY UPDATE balance=balance+%s
        """, (user_id, amount, amount))
        conn.commit()
    finally:
        cur.close(); conn.close()


def deduct_credit(user_id, amount):
    conn = get_connection(); cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE wallet
            SET balance=balance-%s
            WHERE user_id=%s AND balance >= %s
        """, (amount, user_id, amount))
        conn.commit()
        return cur.rowcount > 0
    finally:
        cur.close(); conn.close()


def decrease_stock(product_id):
    return decrease_product_stock(product_id, 1) > 0


def _new_order_number():
    return "PRN-" + datetime.now().strftime("%Y%m%d%H%M%S%f")


def purchase_product(user_id, product_id, address="", description="خرید مستقیم از تلگرام"):
    """Atomic direct purchase using the live DB schema."""
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()

        cur.execute("""
            SELECT id, product_code, name, price, stock
            FROM products
            WHERE id=%s
            FOR UPDATE
        """, (product_id,))
        product = cur.fetchone()
        if not product:
            raise ValueError("محصول پیدا نشد.")
        if int(product["stock"]) < 1:
            raise ValueError("موجودی محصول کافی نیست.")

        cur.execute("SELECT user_id, balance FROM wallet WHERE user_id=%s FOR UPDATE", (user_id,))
        wallet = cur.fetchone()
        if not wallet:
            raise ValueError("کیف پول کاربر پیدا نشد.")

        price = float(product["price"])
        balance = float(wallet["balance"])
        if balance < price:
            raise ValueError("اعتبار کافی نیست.")

        order_number = _new_order_number()
        cur.execute("""
            INSERT INTO orders
            (order_number,user_id,status,total_price,address,description)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (order_number, user_id, "completed", price, address or "", description or ""))
        order_id = cur.lastrowid

        # Live DB column is unit_price.
        cur.execute("""
            INSERT INTO order_items
            (order_id,product_id,quantity,unit_price)
            VALUES (%s,%s,%s,%s)
        """, (order_id, product_id, 1, price))

        cur.execute("UPDATE products SET stock=stock-1 WHERE id=%s AND stock>=1", (product_id,))
        if cur.rowcount != 1:
            raise ValueError("موجودی محصول تغییر کرده است. دوباره تلاش کنید.")

        cur.execute("UPDATE wallet SET balance=balance-%s WHERE user_id=%s AND balance>=%s",
                    (price, user_id, price))
        if cur.rowcount != 1:
            raise ValueError("اعتبار کافی نیست یا اعتبار تغییر کرده است.")

        conn.commit()
        return {
            "order_id": order_id,
            "order_number": order_number,
            "product_name": product["name"],
            "product_code": product["product_code"],
            "price": price,
            "new_stock": int(product["stock"]) - 1,
            "new_balance": balance - price,
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close(); conn.close()


def checkout_cart_transaction(user_id, address="", description="خرید از سبد خرید"):
    """Atomically buy every item in carts for the user."""
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()

        cur.execute("""
            SELECT c.id AS cart_id, c.product_id, c.quantity,
                   p.name, p.product_code, p.price, p.stock
            FROM carts c
            INNER JOIN products p ON c.product_id=p.id
            WHERE c.user_id=%s
            ORDER BY c.id
            FOR UPDATE
        """, (user_id,))
        items = cur.fetchall()
        if not items:
            raise ValueError("سبد خرید شما خالی است.")

        cur.execute("SELECT balance FROM wallet WHERE user_id=%s FOR UPDATE", (user_id,))
        wallet = cur.fetchone()
        if not wallet:
            raise ValueError("کیف پول کاربر پیدا نشد.")

        total = 0.0
        for item in items:
            qty = int(item["quantity"])
            stock = int(item["stock"])
            if qty < 1:
                raise ValueError("تعداد یکی از محصولات نامعتبر است.")
            if stock < qty:
                raise ValueError(f"موجودی {item['name']} برای تعداد درخواستی کافی نیست.")
            total += float(item["price"]) * qty

        balance = float(wallet["balance"])
        if balance < total:
            raise ValueError(f"اعتبار کافی نیست. مبلغ مورد نیاز: {total:,.2f}")

        order_number = _new_order_number()
        cur.execute("""
            INSERT INTO orders
            (order_number,user_id,status,total_price,address,description)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (order_number, user_id, "completed", total, address or "", description or ""))
        order_id = cur.lastrowid

        for item in items:
            qty = int(item["quantity"])
            price = float(item["price"])
            cur.execute("""
                INSERT INTO order_items
                (order_id,product_id,quantity,unit_price)
                VALUES (%s,%s,%s,%s)
            """, (order_id, item["product_id"], qty, price))
            cur.execute("""
                UPDATE products SET stock=stock-%s
                WHERE id=%s AND stock>=%s
            """, (qty, item["product_id"], qty))
            if cur.rowcount != 1:
                raise ValueError(f"موجودی {item['name']} تغییر کرده است.")

        cur.execute("UPDATE wallet SET balance=balance-%s WHERE user_id=%s AND balance>=%s",
                    (total, user_id, total))
        if cur.rowcount != 1:
            raise ValueError("اعتبار کافی نیست یا اعتبار تغییر کرده است.")

        cur.execute("DELETE FROM carts WHERE user_id=%s", (user_id,))
        conn.commit()

        return {
            "order_id": order_id,
            "order_number": order_number,
            "total": total,
            "new_balance": balance - total,
            "items": items,
        }
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close(); conn.close()
