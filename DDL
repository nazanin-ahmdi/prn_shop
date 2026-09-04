import mysql.connector
from config import database_config, database


def create_database():
    conn = mysql.connector.connect(**database_config)
    cursor = conn.cursor()

    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS `{database}` "
        "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )

    conn.commit()
    cursor.close()
    conn.close()

    print("Database created successfully.")


def create_tables():
    conn = mysql.connector.connect(
        **database_config,
        database=database
    )
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            telegram_id BIGINT NOT NULL UNIQUE,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            username VARCHAR(100),
            phone VARCHAR(20),
            address TEXT,
            role ENUM('user', 'admin') DEFAULT 'user',
            register_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_update DATETIME DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(150) NOT NULL UNIQUE,
            description TEXT,
            register_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_update DATETIME DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_code VARCHAR(50) NOT NULL UNIQUE,
            name VARCHAR(200) NOT NULL,
            description TEXT,
            category_id INT,
            price DECIMAL(15,2) NOT NULL DEFAULT 0,
            stock INT NOT NULL DEFAULT 0,
            register_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_update DATETIME DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id)
                REFERENCES categories(id)
                ON DELETE SET NULL
                ON UPDATE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wallets (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL UNIQUE,
            balance DECIMAL(15,2) NOT NULL DEFAULT 0,
            register_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_update DATETIME DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS carts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            product_id INT NOT NULL,
            quantity INT NOT NULL DEFAULT 1,
            register_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_update DATETIME DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_user_product (user_id, product_id),
            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            FOREIGN KEY (product_id)
                REFERENCES products(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            order_number VARCHAR(50) NOT NULL UNIQUE,
            user_id INT NOT NULL,
            status VARCHAR(50) NOT NULL DEFAULT 'pending',
            total_price DECIMAL(15,2) NOT NULL DEFAULT 0,
            address TEXT,
            description TEXT,
            register_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_update DATETIME DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            order_id INT NOT NULL,
            product_id INT NOT NULL,
            quantity INT NOT NULL DEFAULT 1,
            unit_price DECIMAL(15,2) NOT NULL DEFAULT 0,
            register_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id)
                REFERENCES orders(id)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            FOREIGN KEY (product_id)
                REFERENCES products(id)
                ON DELETE RESTRICT
                ON UPDATE CASCADE
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()

    print("All tables created successfully.")


if __name__ == "__main__":
    create_database()
    create_tables()
    print("PRN-Shop database setup completed.")
