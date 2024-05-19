"""Order Database"""

import sqlite3


class OrderDatabase:
    def __init__(self, db_file="orders.db"):
        self.conn = sqlite3.connect(
            db_file
        )  # Connect to database (or create if not exists)

    def close(self):
        self.conn.close()

    def load_fake_data(self):
        cursor = self.conn.cursor()

        # Create a table with fake customer orders
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_name TEXT,
            product_name TEXT,
            quantity INTEGER,
            price REAL,
            status TEXT
        )
        """
        )

        # Insert some fake demo data
        orders = [
            ("ORD12345", "Alice", "Laptop", 1, 999.99, "Shipped"),
            ("ORD12346", "Bob", "Smartphone", 2, 499.99, "Processing"),
            ("ORD12347", "Charlie", "Headphones", 1, 199.99, "Delivered"),
        ]

        cursor.executemany(
            "INSERT OR IGNORE INTO orders VALUES (?, ?, ?, ?, ?, ?)", orders
        )

        # Commit the changes and close the connection
        self.conn.commit()

    def get_order_status(self, order_id: str):
        """Retrieves the current order status"""
        try:
            cursor = self.conn.execute(
                "SELECT status FROM orders WHERE order_id = ?", (order_id,)
            )
            row = cursor.fetchone()
            return row[0] if row else "Order not found"
        except sqlite3.Error as e:
            return f"Database error: {str(e)}"
