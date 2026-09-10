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

def insert_order_item(
        order_id,
        product_id,
        quantity,
        unit_price):

    conn = get_connection()
    cur = conn.cursor()

    sql = """
    INSERT INTO order_items
    (
        order_id,
        product_id,
        quantity,
        unit_price
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
        unit_price
    )

    cur.execute(sql, data)
    conn.commit()
    print("Order Item Added.")

    cur.close()
    conn.close()

def insert_cart(user_id,
                product_id,
                quantity):

    conn = get_connection()
    cur = conn.cursor()

    sql = """
    INSERT INTO carts
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

def add_to_cart(user_id, product_id, quantity=1):

    conn = get_connection()
    cur = conn.cursor()

    sql_check = """
    SELECT id, quantity
    FROM carts
    WHERE user_id = %s AND product_id = %s
    """
    cur.execute(sql_check, (user_id, product_id))
    existing_item = cur.fetchone()

    if existing_item:

        cart_id = existing_item[0]
        current_quantity = existing_item[1]

        sql_update = """
        UPDATE carts
        SET quantity = %s
        WHERE id = %s
        """

        cur.execute(
            sql_update,
            (current_quantity + quantity, cart_id)
        )

    else:

        sql_insert = """
        INSERT INTO carts
        (user_id, product_id, quantity)
        VALUES (%s, %s, %s)
        """

        cur.execute(
            sql_insert,
            (user_id, product_id, quantity)
        )

    conn.commit()

    cur.close()
    conn.close()

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
    UPDATE carts
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
    DELETE FROM carts
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
    FROM carts
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
        UPDATE carts
        SET quantity = %s
        WHERE id = %s
        """

        cur.execute(
            sql_update,
            (current_quantity + quantity, cart_id)
        )

    else:

        sql_insert = """
        INSERT INTO carts
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



def process_direct_purchase(user_id, product_id):
    """Atomically create a direct order, deduct wallet credit and stock."""
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()
        cur.execute("SELECT id, name, price, stock FROM products WHERE id=%s FOR UPDATE", (product_id,))
        product = cur.fetchone()
        if not product or int(product['stock']) < 1:
            conn.rollback(); return False, 'OUT_OF_STOCK'
        cur.execute("SELECT balance FROM wallet WHERE user_id=%s FOR UPDATE", (user_id,))
        wallet = cur.fetchone()
        balance = float(wallet['balance']) if wallet else 0.0
        price = float(product['price'])
        if balance < price:
            conn.rollback(); return False, 'INSUFFICIENT_CREDIT'
        order_number = f"ORD-{int(time.time() * 1000)}-{user_id}"
        cur.execute("""INSERT INTO orders (order_number,user_id,status,total_price,address,description)
                       VALUES (%s,%s,%s,%s,%s,%s)""",
                    (order_number,user_id,'completed',price,'','خرید مستقیم از تلگرام'))
        order_id = cur.lastrowid
        cur.execute("INSERT INTO order_items (order_id,product_id,quantity,unit_price) VALUES (%s,%s,%s,%s)",
                    (order_id,product_id,1,price))
        cur.execute("UPDATE products SET stock=stock-1 WHERE id=%s AND stock>0", (product_id,))
        if cur.rowcount != 1: raise RuntimeError('STOCK_UPDATE_FAILED')
        cur.execute("UPDATE wallet SET balance=balance-%s WHERE user_id=%s AND balance>=%s", (price,user_id,price))
        if cur.rowcount != 1: raise RuntimeError('WALLET_UPDATE_FAILED')
        conn.commit()
        return True, {'order_number':order_number,'order_id':order_id,'name':product['name'],'price':price,'new_balance':balance-price}
    except Exception as e:
        conn.rollback(); print('DIRECT PURCHASE ERROR:', e); return False, str(e)
    finally:
        cur.close(); conn.close()


def process_cart_checkout(user_id):
    """Atomically purchase every item currently in carts."""
    conn = get_connection(); cur = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()
        cur.execute("""SELECT c.id AS cart_id,c.product_id,c.quantity,p.name,p.price,p.stock
                       FROM carts c JOIN products p ON p.id=c.product_id
                       WHERE c.user_id=%s FOR UPDATE""", (user_id,))
        items=cur.fetchall()
        if not items: conn.rollback(); return False,'EMPTY_CART'
        total=sum(float(x['price'])*int(x['quantity']) for x in items)
        for x in items:
            if int(x['quantity']) > int(x['stock']): conn.rollback(); return False,f"OUT_OF_STOCK:{x['name']}"
        cur.execute("SELECT balance FROM wallet WHERE user_id=%s FOR UPDATE", (user_id,)); w=cur.fetchone()
        bal=float(w['balance']) if w else 0.0
        if bal < total: conn.rollback(); return False,'INSUFFICIENT_CREDIT'
        order_number=f"ORD-{int(time.time()*1000)}-{user_id}"
        cur.execute("INSERT INTO orders (order_number,user_id,status,total_price,address,description) VALUES (%s,%s,%s,%s,%s,%s)",(order_number,user_id,'completed',total,'','خرید از سبد تلگرام'))
        order_id=cur.lastrowid
        for x in items:
            cur.execute("INSERT INTO order_items (order_id,product_id,quantity,unit_price) VALUES (%s,%s,%s,%s)",(order_id,x['product_id'],x['quantity'],x['price']))
            cur.execute("UPDATE products SET stock=stock-%s WHERE id=%s AND stock>=%s",(x['quantity'],x['product_id'],x['quantity']))
            if cur.rowcount != 1: raise RuntimeError('STOCK_UPDATE_FAILED')
        cur.execute("UPDATE wallet SET balance=balance-%s WHERE user_id=%s AND balance>=%s",(total,user_id,total))
        if cur.rowcount != 1: raise RuntimeError('WALLET_UPDATE_FAILED')
        cur.execute("DELETE FROM carts WHERE user_id=%s",(user_id,))
        conn.commit(); return True,{'order_number':order_number,'order_id':order_id,'total':total,'new_balance':bal-total}
    except Exception as e:
        conn.rollback(); print('CART CHECKOUT ERROR:',e); return False,str(e)
    finally:
        cur.close(); conn.close()
