import asyncpg
from sendo.sendo_database import insert_product_data,psycopg2, hostname, username, pwd, port_id # Ensure this is async or refactor accordingly

async def reset_table(conn):
    """
    Asynchronously reset the `products` table by truncating it.
    """
    try:
        await conn.execute("TRUNCATE TABLE products RESTART IDENTITY;")
        print("Table `products` truncated successfully.")
    except Exception as e:
        print("Error while truncating table:", e)

async def save_products_to_db(products, reset_flag=False):
    """
    Asynchronously save products to the database.
    
    Args:
        products (list): A list of product data to save.
        reset_flag (bool): Whether to reset the table before inserting data.
    """
    try:
        conn = await asyncpg.connect(
            host=hostname,
            database='sendo_practice_database',
            user=username,
            password=pwd,
            port=port_id
        )
        print("Database connection established successfully.")

        # Reset the table if the flag is set
        if reset_flag:
            await reset_table(conn)

        # Insert the product data
        await insert_product_data(conn, products)  # Ensure `insert_product_data` is asynchronous
        print("Data saved to the database successfully.")

        await conn.close()
    except Exception as e:
        print("Error while saving products to the database:", e)