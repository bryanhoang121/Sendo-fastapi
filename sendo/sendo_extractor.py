from requests_html import AsyncHTMLSession
import re
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import asyncio
from concurrent.futures import ThreadPoolExecutor


async def fetch_product_details(product_url, render_attempts=3): #fetch_product_details_async
    """
    Fetch and extract details from a single product page asynchronously, including handling the 'See Full Description' button.
    """
    product_name = "N/A"
    product_price_range = "N/A"
    product_brand = "N/A"
    product_sold = "N/A"
    rating_value = "N/A"
    rating_count = "N/A"
    combinations = []
    description_text = "N/A"
    combined_paragraph = ""

    session = AsyncHTMLSession()

    try:
        # Fetch the page
        product_page = await session.get(product_url)

        # Render the page
        for attempt in range(render_attempts):
            try:
                await product_page.html.arender(sleep=60)  # Async rendering
                break
            except Exception as e:
                print(f"Render attempt {attempt + 1} failed for {product_url}: {e}")
        else:
            raise Exception(f"Failed to render product page after {render_attempts} attempts: {product_url}")

        # Save product HTML for debugging (optional)
        with open("product_debug.html", "w", encoding="utf-8") as file:
            file.write(product_page.html.html)
        print("Waiting for the page to load...")
        time.sleep(20)  # Adjust the duration based on actual load time


        # Extract product details
        print("fetching product name")
        product_name_element = product_page.html.xpath('//h1[contains(@class, "d7ed-ytwGPk")]', first=True)
        product_name = product_name_element.text if product_name_element else "N/A"
        print("fetching product price range")
        product_price_element = product_page.html.xpath('//span[contains(@class, "d7ed-giDKVr")]', first=True)
        product_price_range = product_price_element.text if product_price_element else "N/A"
        print("fetching product brand")
        product_brand_element = product_page.html.xpath('//div[contains(@class, "BsdHC7")]//span[contains(@class, "p8je0n")]', first=True)
        product_brand = product_brand_element.text if product_brand_element else "N/A"
        print("fetching product sold")
        product_sold_element = product_page.html.xpath('//span[contains(@class, "_3141-TWaO5A") and contains(@class, "d7ed-KXpuoS")]', first=True)
        product_sold = product_sold_element.text if product_sold_element else "N/A"

        rating_value = "N/A"
        rating_count = "N/A"
        try:
            # Look for JSON-LD in a <script> tag
            script_match = re.search(r'"aggregateRating":\{.*?\}', product_page.html.html)
            if script_match:
                aggregate_data = json.loads("{" + script_match.group(0) + "}")
                print("fetching product rating value and rating count")
                rating_value = aggregate_data.get("aggregateRating", {}).get("ratingValue", "N/A")
                rating_count = aggregate_data.get("aggregateRating", {}).get("ratingCount", "N/A")
        except Exception as e:
            print(f"Error parsing rating data: {e}")

        # Use Selenium for interaction
        # Initialize WebDriver with notification settings
        options = Options()
        prefs = {"profile.default_content_setting_values.notifications": 2}  # Block notifications
        options.add_experimental_option("prefs", prefs)
        driver = webdriver.Chrome(options=options)  # Initialize WebDriver with options
        notification_handled = False 
        driver.get(product_url)  # Load the product page


        try:
            print("Waiting for the page to load...")
            time.sleep(15)  # Adjust the duration based on actual load time

            print("Fetching all color and type combinations...")

            # Store results
            combinations = []
            unique_combinations = set()  # To track unique results

            # Locate the parent <div> for colors
            try:
                color_container = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '(//div[contains(@class, "d7ed-TmQak_")])[1]'))
                )
                color_buttons = color_container.find_elements(By.XPATH, './/button[@aria-label="select-attribute"]')
                print(f"Found {len(color_buttons)} color buttons.")
            except Exception as e:
                print("No color container found or failed to load colors:", e)
                color_buttons = []

            # Locate the parent <div> for types
            try:
                type_container = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '(//div[contains(@class, "d7ed-TmQak_")])[2]'))
                )
                type_buttons = type_container.find_elements(By.XPATH, './/button[@aria-label="select-attribute"]')
                print(f"Found {len(type_buttons)} type buttons.")
            except Exception as e:
                print("No type container found or failed to load types:", e)
                type_buttons = []

            # Iterate over each color
            for i, color_button in enumerate(color_buttons):
                # Dealing with notification
                if not notification_handled:
                    try:
                        modal_close_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//span[@role='presentation']"))
                        )
                        modal_close_button.click()
                        print("'How to enable notifications' modal closed successfully.")
                        notification_handled = True
                    except Exception as e:
                        print("No 'How to enable notifications' modal detected or failed to close it:", e)

                # Click the current color button
                color_button.click()
                time.sleep(2)  # Wait for the UI to update

                # Extract the updated color text displayed on the page
                try:
                    color_text_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '(//div[@id="select-attribute"]//div[contains(@class, "_3141-xfVUgd")])[1]//span[contains(@class, "d7ed-AHa8cD")]'))
                    )
                    color_text = color_text_element.text.strip()
                    print(f"Selected color: {color_text}")
                except Exception as e:
                    print(f"Failed to fetch the displayed color text: {e}")
                    color_text = "N/A"

                # If types are available, iterate over them
                if type_buttons:
                    for type_button in type_buttons:
                        if not type_button.is_enabled():
                            print(f"Skipping disabled type button for color {color_text}.")
                            continue

                        # Click the type button
                        type_button.click()
                        time.sleep(2)  # Wait for the UI to update

                        # Extract the updated type text displayed on the page
                        try:
                            type_text_element = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, '(//div[@id="select-attribute"]//div[contains(@class, "_3141-xfVUgd")])[2]//span[contains(@class, "d7ed-AHa8cD")]'))
                            )
                            type_text = type_text_element.text.strip()
                            print(f"Selected type: {type_text}")
                        except Exception as e:
                            print(f"Failed to fetch the displayed type text: {e}")
                            type_text = "N/A"

                        # Extract the price for the selected color and type
                        try:
                            price_element = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "_3141-j_1grA")]//span[contains(@class, "d7ed-giDKVr")]'))
                            )
                            price = price_element.text.strip()
                            print(f"Price for {color_text} and {type_text}: {price}")

                            # Add the combination if it's unique
                            combination_key = (color_text, type_text, price)
                            if combination_key not in unique_combinations:
                                unique_combinations.add(combination_key)
                                combinations.append(json.loads(json.dumps({
                                    "color": color_text,
                                    "type": type_text,
                                    "price": price
                                })))
                        except Exception as e:
                            print(f"Failed to fetch price for {color_text} and {type_text}: {e}")
                else:
                    # Handle case where there are no types, just colors
                    try:
                        price_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "_3141-j_1grA")]//span[contains(@class, "d7ed-giDKVr")]'))
                        )
                        price = price_element.text.strip()
                        print(f"Price for {color_text}: {price}")

                        # Add the combination if it's unique
                        combination_key = (color_text, "N/A", price)
                        if combination_key not in unique_combinations:
                            unique_combinations.add(combination_key)
                            combinations.append({
                                "color": color_text,
                                "type": "N/A",
                                "price": price
                            })
                    except Exception as e:
                        print(f"Failed to fetch price for {color_text} (no type): {e}")

            # Handle case where there are types but no colors
            if not color_buttons and type_buttons:
                for type_button in type_buttons:
                    if not type_button.is_enabled():
                        print("Skipping disabled type button.")
                        continue

                    type_button.click()
                    time.sleep(2)  # Wait for the UI to update

                    try:
                        type_text_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '(//div[@id="select-attribute"]//div[contains(@class, "_3141-xfVUgd")])[2]//span[contains(@class, "d7ed-AHa8cD")]'))
                        )
                        type_text = type_text_element.text.strip()
                        print(f"Selected type: {type_text}")
                    except Exception as e:
                        print(f"Failed to fetch the displayed type text: {e}")
                        type_text = "N/A"

                    # Extract price for the type
                    try:
                        price_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "_3141-j_1grA")]//span[contains(@class, "d7ed-giDKVr")]'))
                        )
                        price = price_element.text.strip()
                        print(f"Price for type {type_text}: {price}")

                        # Add the combination if it's unique
                        combination_key = ("N/A", type_text, price)
                        if combination_key not in unique_combinations:
                            unique_combinations.add(combination_key)
                            combinations.append({
                                "color": "N/A",
                                "type": type_text,
                                "price": price
                            })
                            # Ensure `combinations` is serialized into valid JSON
                            combinations = json.loads(json.dumps(combinations))
                    except Exception as e:
                        print(f"Failed to fetch price for type {type_text}: {e}")

            # Print all unique combinations
            print("All unique color-type combinations and prices:")
            for combination in combinations:
                print(combination)

        except Exception as e:
            print(f"Error while fetching color and type combinations: {e}")

        # Extract dynamically rendered content or interact with the page
        try:

            
            # Incrementally scroll to ensure all content is loaded
            print("Scrolling to load the entire description...")
            last_height = driver.execute_script("return document.body.scrollHeight")  # Initial page height
            for _ in range(20):  # Adjust the range for deeper scrolling if needed
                driver.execute_script("window.scrollBy(0, 300);")  # Scroll by 300 pixels
                time.sleep(1)  # Allow rendering
                new_height = driver.execute_script("return document.body.scrollHeight")  # Updated page height
                print(f"Scroll step: New height: {new_height}, Last height: {last_height}")

                # Stop scrolling if no new content is loaded
                if new_height == last_height:
                    print("No more content to load.")
                    break
                last_height = new_height
            # Locate the button in the DOM
            print("Searching for the 'See Full Description' button...")
            see_more_button = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//button[@aria-label="Xem thêm"]'))
            )

            # Scroll to the button
            print("Scrolling to the button...")
            driver.execute_script("arguments[0].scrollIntoView(true);", see_more_button)
            time.sleep(2)  # Allow scrolling to complete

            # Confirm the button is visible
            if not see_more_button.is_displayed():
                raise Exception("Button is not visible after scrolling.")

            # Click the button
            try:
                print("Clicking the 'Xem thêm' button...")
                see_more_button.click()  # Standard click
                print("'Xem thêm' button clicked successfully.")
            except Exception as e:
                print(f"Normal click failed. Trying JavaScript click. Error: {e}")
                driver.execute_script("arguments[0].click();", see_more_button)  # Fallback to JavaScript click
                print("'Xem thêm' button clicked using JavaScript.")
                                        #Dealing with notification
                if not notification_handled:  # Check if notification has been handled
                    try:
                        print("Checking for the 'How to enable notifications' modal...")
                        # Locate the close button (span with role="presentation")
                        modal_close_button = WebDriverWait(driver, 10).until(
                                    EC.element_to_be_clickable((By.XPATH, "//span[@role='presentation']"))
                        )
                        modal_close_button.click()  # Click the close button
                        print("'How to enable notifications' modal closed successfully.")
                        notification_handled = True  # Mark as handled
                    except Exception as e:
                        print("No 'How to enable notifications' modal detected or failed to close it:", e)
            # Skip disabled buttons

            print("'See Full Description' button clicked.")
            # Wait for the description to load and extract it
            description_text = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "_96e1-wAC_05")]'))
            ).text
            print("Description:", description_text)
            # Extract Table Data
            try:
                tables = driver.find_elements(By.XPATH, '//table[contains(@class, "_96e1-t3iHfo")]')
                table_data = []
                for table in tables:
                    # Extract headers
                    headers = [th.text.strip() for th in table.find_elements(By.XPATH, './/thead//th')]
                    # Extract rows
                    rows = table.find_elements(By.XPATH, './/tbody/tr')
                    for row in rows:
                        cells = [td.text.strip() for td in row.find_elements(By.XPATH, './td')]
                        if headers and len(headers) == len(cells):
                            table_data.append(dict(zip(headers, cells)))
                        else:
                            table_data.append(cells)
            except Exception as e:
                print(f"Error extracting table data: {e}")
                table_data = []
            time.sleep(5)
            # Extract List Data
            try:
                lists = driver.find_elements(By.XPATH, '//div[contains(@class, "_96e1-xVRDRz")]//ul')
                list_data = []
                for ul in lists:
                    items = ul.find_elements(By.XPATH, './/li')
                    for item in items:
                        list_item_text = item.text.strip()
                        nested_ul = item.find_elements(By.XPATH, './/ul')
                        if nested_ul:
                            nested_list = [nested.text.strip() for nested in nested_ul]
                            list_data.append({"text": list_item_text, "sublist": nested_list})
                        else:
                            list_data.append({"text": list_item_text})
            except Exception as e:
                print(f"Error extracting list data: {e}")
                list_data = []
                #text after table
            try:
                print("Extracting detailed product information...")

                # Locate the outer <div> containing the nested structure
                main_div = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "_96e1-xVRDRz")]'))
                )

                # Extract text from nested <span>, <p>, and other elements
                paragraphs = main_div.find_elements(By.XPATH, './/p/span')
                extracted_text = []
                for paragraph in paragraphs:
                    text = paragraph.text.strip()
                    if text:  # Only add non-empty text
                        extracted_text.append(text)

                print("Extracted Text:")
                for line in extracted_text:
                    print(line)

            except Exception as e:
                print(f"Error extracting detailed product information: {e}")

            # Combine Data
            description = {
                "text": description_text,
                "table": table_data,
                "list": list_data,
                "text_1": extracted_text
            }
        except Exception as e:
            print(f"Error fetching product details: {e}")
        finally:
            if 'driver' in locals() and driver is not None:
                print("Quitting driver...")
                driver.quit()
        # Combine all text into a single paragraph
        def combine_description_data(description_text, table_data, list_data, extracted_text):
            # Ensure all inputs are strings and sanitize single quotes
            description_text = description_text.replace("'", '"').strip()
            table_values = [str(value).replace("'", '"').strip() for row in table_data for value in (row.values() if isinstance(row, dict) else row)]
            list_values = [str(item.get("text", "")).replace("'", '"').strip() for item in list_data]

            # Combine all text parts
            combined_paragraph = " ".join(
                [description_text] + table_values + list_values + [text.replace("'", '"').strip() for text in extracted_text]
            ).strip()

            return combined_paragraph

        # Generate combined paragraph and replace description
        combined_paragraph = combine_description_data(
            description.get("text", ""),
            description.get("table", []),
            description.get("list", []),
            description.get("text_1", [])
        )

        # Combine all extracted data into a dictionary
        return {
            "name": product_name,
            "price_range": product_price_range,
            "brand": product_brand,
            "sold": product_sold,
            "rating": rating_value,
            "rating_count": rating_count,
            "product_option": json.loads(json.dumps(combinations)),
            "description": combined_paragraph,
            "url": product_url
            
        }

    except Exception as e:
        print(f"Error fetching product details for {product_url}: {e}")
        return {
            "name": product_name,
            "price_range": product_price_range,
            "brand": product_brand,
            "sold": product_sold,
            "rating": rating_value,
            "rating_count": rating_count,
            "product_option": json.loads(json.dumps(combinations)),  # Ensure valid JSON
            "description": combined_paragraph.replace("'", '"'),  # Sanitize single quotes
            "url": product_url
        }

