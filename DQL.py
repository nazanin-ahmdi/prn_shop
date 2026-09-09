from config import get_connection


def get_user_by_telegram_id(telegram_id):
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM users WHERE telegram_id=%s", (telegram_id,))
        return cur.fetchone()
    finally:
        cur.close(); conn.close()


def get_categories():
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM categories")
        return cur.fetchall()
    finally:
        cur.close(); conn.close()


def get_products():
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM products")
        return cur.fetchall()
    finally:
        cur.close(); conn.close()


def get_product_by_id(product_id):
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM products WHERE id=%s", (product_id,))
        return cur.fetchone()
    finally:
        cur.close(); conn.close()


def get_products_by_category(category_title):
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT p.* FROM products p
            INNER JOIN categories c ON p.category_id=c.id
            WHERE c.title=%s ORDER BY p.name
        """, (category_title,))
        return cur.fetchall()
    finally:
        cur.close(); conn.close()


def get_product_by_name(product_name):
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM products WHERE name=%s", (product_name,))
        return cur.fetchone()
    finally:
        cur.close(); conn.close()


def get_users():
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM users")
        return cur.fetchall()
    finally:
        cur.close(); conn.close()


def get_orders():
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT * FROM orders ORDER BY register_date DESC")
        return cur.fetchall()
    finally:
        cur.close(); conn.close()


def get_order_items(order_id):
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT oi.id, oi.order_id, oi.product_id, oi.quantity,
                   oi.unit_price AS price, p.name, p.product_code
            FROM order_items oi
            INNER JOIN products p ON oi.product_id=p.id
            WHERE oi.order_id=%s
        """, (order_id,))
        return cur.fetchall()
    finally:
        cur.close(); conn.close()


def get_cart(user_id):
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT c.id, p.name, c.quantity, p.price
            FROM carts c
            INNER JOIN products p ON c.product_id=p.id
            WHERE c.user_id=%s
            ORDER BY c.register_date DESC
        """, (user_id,))
        return cur.fetchall()
    finally:
        cur.close(); conn.close()


def get_cart_items(user_id):
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT c.id AS cart_id, c.product_id, c.quantity,
                   p.name, p.product_code, p.price, p.stock
            FROM carts c
            INNER JOIN products p ON c.product_id=p.id
            WHERE c.user_id=%s
            ORDER BY c.register_date DESC
        """, (user_id,))
        return cur.fetchall()
    finally:
        cur.close(); conn.close()


def get_cart_item(cart_id):
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT c.id AS cart_id, c.user_id, c.product_id, c.quantity,
                   p.name, p.product_code, p.price, p.stock
            FROM carts c
            INNER JOIN products p ON c.product_id=p.id
            WHERE c.id=%s
        """, (cart_id,))
        return cur.fetchone()
    finally:
        cur.close(); conn.close()


def get_wallet_balance(user_id):
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT balance FROM wallet WHERE user_id=%s", (user_id,))
        wallet = cur.fetchone()
        return wallet["balance"] if wallet else 0
    finally:
        cur.close(); conn.close()
