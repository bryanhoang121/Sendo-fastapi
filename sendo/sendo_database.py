import psycopg2
from psycopg2 import sql
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('config.env')

# Retrieve database connection parameters from environment variables
hostname = os.getenv('DB_HOST')
database = os.getenv('DB_DATABASE')
username = os.getenv('DB_USERNAME')
pwd = os.getenv('DB_PASSWORD')
port_id = int(os.getenv('DB_PORT'))


def create_or_reset_table(reset=False):
    """
    Creates or resets the 'products' table.

    Parameters:
        reset (bool): If True, the table will be reset (dropped and recreated).
    """
    try:
        with psycopg2.connect(
            host=hostname,
            dbname='sendo_practice_database',
            user=username,
            password=pwd,
            port=port_id
        ) as conn:
            with conn.cursor() as cur:
                if reset:
                    # Drop the table if it exists
                    cur.execute("DROP TABLE IF EXISTS products")
                    print("Table 'products' dropped.")

                # Create the table
                create_script = '''CREATE TABLE IF NOT EXISTS products (
                                        id SERIAL PRIMARY KEY,
                                        name TEXT,
                                        price_range TEXT,
                                        brand VARCHAR(255),
                                        sold TEXT,
                                        rating TEXT,
                                        rating_count TEXT,
                                        product_option JSONB,
                                        description TEXT,
                                        url TEXT)'''
                cur.execute(create_script)
                conn.commit()
                print("Table 'products' created or ensured to exist.")
    except Exception as e:
        print(f"Error creating or resetting table: {e}")




async def insert_product_data(conn, products):
    """
    Inserts a list of product data into the database asynchronously.

    Parameters:
        conn (asyncpg connection): Active database connection.
        products (list of dicts or tuples): List of product data to insert.
    """
    try:
        product_tuples = []
        for product in products:
            if isinstance(product, dict):
                product_option = product.get("product_option", "{}")  # Default to empty JSON if key missing

                # Debug: Log the original product_option
                print(f"Original product_option: {product_option}")

                # Validate and fix product_option
                if isinstance(product_option, (dict, list)):
                    product_option = json.dumps(product_option)  # Convert dict/list to JSON string
                elif isinstance(product_option, str):
                    try:
                        json.loads(product_option)  # Ensure it's valid JSON
                    except json.JSONDecodeError:
                        product_option = product_option.replace("'", '"')  # Replace single quotes with double quotes
                        try:
                            json.loads(product_option)  # Validate the fixed JSON
                        except json.JSONDecodeError:
                            product_option = "{}"  # Default to empty JSON if still invalid

                # Debug: Log the processed product_option
                print(f"Processed product_option: {product_option}")

                # Prepare the tuple for insertion
                product_tuples.append((
                    str(product.get("name", "N/A")),
                    str(product.get("price_range", "N/A")),
                    str(product.get("brand", "N/A")),
                    str(product.get("sold", "N/A")),
                    str(product.get("rating", "N/A")),
                    str(product.get("rating_count", "N/A")),
                    product_option,  # Valid JSON string
                    str(product.get("description", "N/A")),
                    str(product.get("url", "N/A")),
                ))
            elif isinstance(product, tuple):
                product_tuples.append(product)

        # Insert data into the database asynchronously
        insert_query = '''
            INSERT INTO products (name, price_range, brand, sold, rating, rating_count, product_option, description, url) 
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        '''
        await conn.executemany(insert_query, product_tuples)
        print(f"{len(product_tuples)} products inserted successfully.")
    except Exception as e:
        print(f"Error inserting data into the database: {e}")

if __name__ == "__main__":
    # Reset the table during development/testing
    create_or_reset_table(reset=True)

    # Example data to insert
    example_products = [
        {"name": "Product 1", "price_range": "50", "brand": "Brand A", "sold": "10", "rating": "4.5", "rating_count": "100",
         "product_option": '{"color": "red", "size": "L"}', "description": "Description 1", "url": "http://example.com/1"},
        {"name": "Product 2", "price_range": "100", "brand": "Brand B", "sold": "20", "rating": "4.0", "rating_count": "200",
         "product_option": '[{"color": "blue", "size": "M"}]', "description": "Description 2", "url": "http://example.com/2"},
        {"name": "Product 3", "price_range": "75", "brand": "Brand C", "sold": "15", "rating": "4.8", "rating_count": "300",
         "product_option": '[{"color": "green", "size": "S"}]', "description": "Description 3", "url": "http://example.com/3"},
        # Example tuple data
        ("Product 4", "200", "Brand D", "50", "4.2", "50", '[{"color": "yellow", "size": "XL"}]', "Description 4", "http://example.com/4")
    ]

    # Insert data into the database
    insert_product_data(example_products)