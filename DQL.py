from config import get_connection
def get_user_by_telegram_id(telegram_id):

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
    SELECT *
    FROM users
    WHERE telegram_id=%s
    """
    cur.execute(sql, (telegram_id,))
    result = cur.fetchone()

    cur.close()
    conn.close()
    return result


def get_categories():

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = "SELECT * FROM categories"
    cur.execute(sql)
    result = cur.fetchall()

    cur.close()
    conn.close()
    return result


def get_products():

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
    SELECT *
    FROM products
    """
    cur.execute(sql)
    result = cur.fetchall()

    cur.close()
    conn.close()
    return result


def get_product_by_id(product_id):

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
    SELECT *
    FROM products
    WHERE id=%s
    """

    cur.execute(sql, (product_id,))
    result = cur.fetchone()

    cur.close()
    conn.close()
    return result


def get_products_by_category(category_title):

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
    SELECT p.*
    FROM products p
    INNER JOIN categories c
        ON p.category_id = c.id
    WHERE c.title = %s
    ORDER BY p.name
    """

    cur.execute(sql, (category_title,))
    products = cur.fetchall()

    cur.close()
    conn.close()
    return products

def get_product_by_name(product_name):

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
    SELECT *
    FROM products
    WHERE name=%s
    """

    cur.execute(sql, (product_name,))
    product = cur.fetchone()

    cur.close()
    conn.close()
    return product

def get_users():

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = "SELECT * FROM users"
    cur.execute(sql)

    result = cur.fetchall()

    cur.close()
    conn.close()
    return result

def get_orders():

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
    SELECT *
    FROM orders
    """

    cur.execute(sql)
    result = cur.fetchall()

    cur.close()
    conn.close()
    return result

def get_order_items(order_id):

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
    SELECT
        oi.id,
        oi.order_id,
        oi.product_id,
        oi.quantity,
        oi.unit_price,
        p.name,
        p.product_code
    FROM order_items oi
    INNER JOIN products p
        ON oi.product_id = p.id
    WHERE oi.order_id = %s
    """

    cur.execute(sql, (order_id,))
    items = cur.fetchall()

    cur.close()
    conn.close()
    return items

def get_cart(user_id):

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
    SELECT
        c.id,
        p.name,
        c.quantity,
        p.price
    FROM carts c
    INNER JOIN products p
    ON c.product_id = p.id
    WHERE c.user_id=%s
    """

    cur.execute(sql, (user_id,))
    result = cur.fetchall()

    cur.close()
    conn.close()
    return result

def get_cart_items(user_id):

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
    SELECT
        c.id AS cart_id,
        c.product_id,
        c.quantity,
        p.name,
        p.product_code,
        p.price,
        p.stock
    FROM carts c
    INNER JOIN products p
        ON c.product_id = p.id
    WHERE c.user_id = %s
    ORDER BY c.register_date DESC
    """

    cur.execute(sql, (user_id,))
    items = cur.fetchall()

    cur.close()
    conn.close()
    return items

def get_cart_item(cart_id):

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
    SELECT
        c.id AS cart_id,
        c.user_id,
        c.product_id,
        c.quantity,
        p.name,
        p.product_code,
        p.price,
        p.stock
    FROM carts c
    INNER JOIN products p
        ON c.product_id = p.id
    WHERE c.id = %s
    """

    cur.execute(sql, (cart_id,))
    item = cur.fetchone()

    cur.close()
    conn.close()
    return item

def get_wallet_balance(user_id):

    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    sql = """
    SELECT balance
    FROM wallet
    WHERE user_id = %s
    """

    cur.execute(sql, (user_id,))
    wallet = cur.fetchone()

    cur.close()
    conn.close()

    if wallet is None:
        return 0

    return wallet["balance"]
