from config import get_connection


def register_user(message):

    user = message.from_user

    conn = get_connection()

    cur = conn.cursor()

    sql = """
    INSERT INTO users
    (
        telegram_id,
        first_name,
        last_name,
        username,
        phone,
        address
    )
    VALUES
    (
        %s,%s,%s,%s,%s,%s
    )
    """

    data = (
        user.id,
        user.first_name,
        user.last_name,
        user.username,
        None,
        None
    )

    cur.execute(sql, data)

    conn.commit()

    cur.close()
    conn.close()



# ==========================
# Categories
# ==========================

def insert_category(title, parent_id=None):
    conn = get_connection()
    cur = conn.cursor()

    sql = """
    INSERT INTO categories(title, parent_id)
    VALUES (%s,%s)
    """

    cur.execute(sql, (title, parent_id))
    conn.commit()

    print("Category Added.")

    cur.close()
    conn.close()


# ==========================
# Products
# ==========================

def insert_product(product_code,
                   category_id,
                   name,
                   description,
                   price,
                   stock,
                   minimum_stock):

    conn = get_connection()
    cur = conn.cursor()

    sql = """
    INSERT INTO products
    (
        product_code,
        category_id,
        name,
        description,
        price,
        stock,
        minimum_stock
    )
    VALUES
    (
        %s,%s,%s,%s,%s,%s,%s
    )
    """

    data = (
        product_code,
        category_id,
        name,
        description,
        price,
        stock,
        minimum_stock
    )

    cur.execute(sql, data)

    conn.commit()

    print("Product Added.")

    cur.close()
    conn.close()


# ==========================
# Users
# ==========================

def insert_user(
        telegram_id,
        first_name,
        last_name,
        username,
        phone,
        address):

    conn = get_connection()
    cur = conn.cursor()

    sql = """
    INSERT INTO users
    (
        telegram_id,
        first_name,
        last_name,
        username,
        phone,
        address
    )

    VALUES
    (
        %s,%s,%s,%s,%s,%s
    )
    """

    data = (
        telegram_id,
        first_name,
        last_name,
        username,
        phone,
        address
    )

    cur.execute(sql, data)

    conn.commit()

    print("User Added.")

    cur.close()
    conn.close()


# ==========================
# Orders
# ==========================

def insert_order(
        order_number,
        user_id,
        status,
        total_price,
        address,
        description):

    conn = get_connection()
    cur = conn.cursor()

    sql = """
    INSERT INTO orders
    (
        order_number,
        user_id,
        status,
        total_price,
        address,
        description
    )
    VALUES
    (
        %s, %s, %s, %s, %s, %s
    )
    """

    data = (
        order_number,
        user_id,
        status,
        total_price,
        address,
        description
    )

    cur.execute(sql, data)

    conn.commit()

    order_id = cur.lastrowid

    print("Order Added:", order_id)

    cur.close()
    conn.close()

    return order_id
# ==========================
# Order Items
# ==========================

def insert_order_item(
        order_id,
        product_id,
        quantity,
        price):

    conn = get_connection()
    cur = conn.cursor()

    sql = """
    INSERT INTO order_items
    (
        order_id,
        product_id,
        quantity,
        price
    )

    VALUES
    (
        %s,%s,%s,%s
    )
    """

    data = (
        order_id,
        product_id,
        quantity,
        price
    )

    cur.execute(sql, data)

    conn.commit()

    print("Order Item Added.")

    cur.close()
    conn.close()


# ==========================
# Cart
# ==========================

def insert_cart(user_id,
                product_id,
                quantity):

    conn = get_connection()
    cur = conn.cursor()

    sql = """
    INSERT INTO cart
    (
        user_id,
        product_id,
        quantity
    )

    VALUES
    (
        %s,%s,%s
    )
    """

    cur.execute(sql, (user_id, product_id, quantity))

    conn.commit()

    print("Added To Cart.")

    cur.close()
    conn.close()

def add_to_cart(user_id, product_id):

    conn = get_connection()
    cur = conn.cursor()

    # Check if product already exists in user's cart
    sql_check = """
    SELECT id, quantity
    FROM cart
    WHERE user_id = %s AND product_id = %s
    """

    cur.execute(sql_check, (user_id, product_id))

    existing_item = cur.fetchone()

    if existing_item:

        cart_id = existing_item[0]
        current_quantity = existing_item[1]

        sql_update = """
        UPDATE cart
        SET quantity = %s
        WHERE id = %s
        """

        cur.execute(
            sql_update,
            (current_quantity + 1, cart_id)
        )

    else:

        sql_insert = """
        INSERT INTO cart
        (user_id, product_id, quantity)
        VALUES (%s, %s, %s)
        """

        cur.execute(
            sql_insert,
            (user_id, product_id, 1)
        )

    conn.commit()

    cur.close()
    conn.close()
# ==========================
# Stock Notification
# ==========================

def insert_stock_notification(
        user_id,
        product_id):

    conn = get_connection()
    cur = conn.cursor()

    sql = """
    INSERT INTO stock_notifications
    (
        user_id,
        product_id
    )

    VALUES
    (
    %s,%s
    )
    """

    cur.execute(sql, (user_id, product_id))

    conn.commit()

    print("Notification Saved.")

    cur.close()
    conn.close()

def update_cart_quantity(cart_id, quantity):

    conn = get_connection()
    cur = conn.cursor()

    sql = """
    UPDATE cart
    SET quantity = %s
    WHERE id = %s
    """

    cur.execute(sql, (quantity, cart_id))

    conn.commit()

    cur.close()
    conn.close()

def remove_from_cart(cart_id):

    conn = get_connection()
    cur = conn.cursor()

    sql = """
    DELETE FROM cart
    WHERE id = %s
    """

    cur.execute(sql, (cart_id,))

    conn.commit()

    cur.close()
    conn.close()

def decrease_product_stock(product_id, quantity):

    conn = get_connection()
    cur = conn.cursor()

    sql = """
    UPDATE products
    SET stock = stock - %s
    WHERE id = %s
    AND stock >= %s
    """

    cur.execute(
        sql,
        (quantity, product_id, quantity)
    )

    conn.commit()

    affected_rows = cur.rowcount

    cur.close()
    conn.close()

    return affected_rows
def add_existing_product_to_cart(user_id, product_id, quantity):

    conn = get_connection()
    cur = conn.cursor()

    sql_check = """
    SELECT id, quantity
    FROM cart
    WHERE user_id = %s
    AND product_id = %s
    """

    cur.execute(
        sql_check,
        (user_id, product_id)
    )

    existing_item = cur.fetchone()

    if existing_item:

        cart_id = existing_item[0]
        current_quantity = existing_item[1]

        sql_update = """
        UPDATE cart
        SET quantity = %s
        WHERE id = %s
        """

        cur.execute(
            sql_update,
            (current_quantity + quantity, cart_id)
        )

    else:

        sql_insert = """
        INSERT INTO cart
        (
            user_id,
            product_id,
            quantity
        )
        VALUES
        (
            %s, %s, %s
        )
        """

        cur.execute(
            sql_insert,
            (user_id, product_id, quantity)
        )

    conn.commit()

    cur.close()
    conn.close()

def create_wallet(user_id):

    conn = get_connection()
    cur = conn.cursor()

    sql = """
    INSERT INTO wallet
    (
        user_id,
        balance
    )
    VALUES
    (
        %s,
        %s
    )
    """

    cur.execute(
        sql,
        (user_id, 0)
    )

    conn.commit()

    cur.close()
    conn.close()

def increase_wallet_balance(user_id, amount):

    conn = get_connection()
    cur = conn.cursor()

    sql = """
    UPDATE wallet
    SET balance = balance + %s
    WHERE user_id = %s
    """

    cur.execute(
        sql,
        (amount, user_id)
    )

    conn.commit()

    cur.close()
    conn.close()


def add_credit(user_id, amount):

    conn = get_connection()
    cur = conn.cursor()

    sql = """
    INSERT INTO wallet (user_id, balance)
    VALUES (%s, %s)
    ON DUPLICATE KEY UPDATE
        balance = balance + %s
    """

    cur.execute(
        sql,
        (user_id, amount, amount)
    )

    conn.commit()

    cur.close()
    conn.close()
def deduct_credit(user_id, amount):

    conn = get_connection()
    cur = conn.cursor()

    print("DEDUCT CREDIT")
    print("USER ID:", user_id)
    print("AMOUNT:", amount)

    sql = """
    UPDATE wallet
    SET balance = balance - %s
    WHERE user_id = %s
    """

    cur.execute(
        sql,
        (amount, user_id)
    )

    print("ROWS UPDATED:", cur.rowcount)

    conn.commit()

    affected_rows = cur.rowcount

    cur.close()
    conn.close()

    return affected_rows > 0

def decrease_stock(product_id):

    conn = get_connection()
    cur = conn.cursor()

    sql = """
    UPDATE products
    SET stock = stock - 1
    WHERE id = %s
      AND stock > 0
    """

    cur.execute(
        sql,
        (product_id,)
    )

    conn.commit()

    affected_rows = cur.rowcount

    cur.close()
    conn.close()

    return affected_rows > 0

