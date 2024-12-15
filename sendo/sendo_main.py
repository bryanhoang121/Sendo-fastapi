import time
import json
import asyncio
from sendo.sendo_session import fetch_product_links  # Ensure this is async
from sendo.sendo_extractor import fetch_product_details  # Ensure this is async
from sendo.db_connection import save_products_to_db  # Update if async
import psycopg2

async def process_products(url, reset=False):
    """
    Processes products by fetching data from the provided URL.
    Optionally resets the database table.

    Parameters:
        url (str): The URL to scrape products from.how to 
        reset (bool): Whether to reset the database table.
    Returns:
        dict: A summary of the operation, including product count.
    """
    product_data = []

    # Fetch product links asynchronously
    print("Fetching product links...")
    product_urls = await fetch_product_links(url)  # Await the async function
    print(f"Found {len(product_urls)} product URLs.")

    # Process individual products asynchronously
    # Process individual products asynchronously
    for index, product_url in enumerate(product_urls[:2]):  # Limit for testing
        print(f"Product URLs to process: {index}")
        try:
            print(f"Original URL: {product_url}")
            if not product_url.startswith("http"):
                product_url = f"https://www.sendo.vn{product_url}"
            print(f"Fetching product {index + 1}: {product_url}")
            product_details = await fetch_product_details(product_url)  # Await the async function
            print(f"Fetched details for product {index + 1}: {product_details}")
            product_data.append(product_details)
            await asyncio.sleep(2)  # Avoid overloading the server
        except Exception as e:
            print(f"Error processing product {index + 1}: {e}")

    # Save data to the database asynchronously
    try:
        await save_products_to_db(product_data, reset_flag=reset)  # Ensure save_products_to_db is async
        print("Data saved to the database successfully.")
    except Exception as e:
        print(f"Error saving data to the database: {e}")

    return {"product_count": len(product_data), "products": product_data}