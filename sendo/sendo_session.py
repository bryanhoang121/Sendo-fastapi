from playwright.async_api import async_playwright


async def fetch_product_links(url: str, scrolldown: int = 4):
    """
    Fetch and render the main page using Playwright (Async), then extract product links.

    Args:
        url (str): The URL of the page to scrape.
        scrolldown (int): Number of times to scroll bbdown to load more content.

    Returns:
        list: A list of product URLs extracted from the page.
    """
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)  # Set headless=False for debugging
        page = await browser.new_page()
        await page.goto(url, timeout=100000)

        # Scroll down to load dynamic content
        for _ in range(scrolldown):
            await page.mouse.wheel(0, 1000)  # Scroll down
            await page.wait_for_timeout(5000)  # Allow content to load

        # Wait for at least one product container to ensure content is loaded
        await page.wait_for_selector('//div[contains(@class, "d7ed-d4keTB")]', timeout=10000)

        # Extract links using the corrected XPath
        links = page.locator('//div[contains(@class, "d7ed-d4keTB") and contains(@class, "d7ed-OoK3wU")]//a[@href]')
        product_links = await links.evaluate_all("elements => elements.map(el => el.href)")  # Extract href attributes

        print(f"Found {len(product_links)} product links.")
        await browser.close()

        # Print and return the product links
        for product_link in product_links:
            print(product_link)

        return product_links