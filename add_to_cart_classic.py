"""
Add to Cart - Classic Playwright Approach
Uses direct DOM interaction instead of computer vision.
"""

import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def handle_cookie_popup(page):
    """
    Handle cookie consent popup if present.

    This function tries to find and click cookie acceptance buttons.
    It uses a short timeout to fail fast if no popup exists.

    Args:
        page: Playwright page object

    Returns:
        bool: True if popup was handled, False if no popup found
    """
    # Common cookie popup selectors (Amazon and general patterns)
    cookie_selectors = [
        "#sp-cc-accept",  # Amazon's "Accept Cookies" button
        "button:has-text('Accept')",
        "button:has-text('Accept Cookies')",
        "button:has-text('I agree')",
        "button:has-text('Accept all')",
        "input[name='accept']",
        "#accept-cookie-button",
        ".cookie-accept",
        ".accept-cookies",
    ]

    for selector in cookie_selectors:
        try:
            # Try to find the button with a short timeout
            button = page.locator(selector).first
            if button.is_visible(timeout=2000):
                print(f"Found cookie popup with selector: {selector}")
                button.click()
                print("✓ Cookie popup handled")
                # Wait a moment for the popup to close
                time.sleep(0.5)
                return True
        except Exception:
            # Selector not found or not visible, try next one
            continue

    print("No cookie popup detected (or already handled)")
    return False


def add_to_cart(page, url):
    """
    Navigate to a product page and click the add-to-cart button using DOM selectors.

    Uses multiple selector strategies to handle:
    - Dynamic ID suffixes (e.g., add-to-cart-button-ubb)
    - Different text variations ("Add to Cart" vs "Add to basket")
    - Anti-bot protection measures

    Args:
        page: Playwright page object
        url: Product page URL

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Navigate to the product page
        print(f"\nNavigating to: {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=30000)

        # Handle cookie popup if present
        handle_cookie_popup(page)

        # Multi-strategy selector approach to handle dynamic IDs and text variations
        # Priority order: most stable selectors first, then fallbacks
        button_selectors = [
            # 1. Input by name attribute (most stable - Amazon rarely changes this)
            ("input[name='submit.add-to-cart']", "name attribute"),

            # 2. Input with ID starting with prefix (catches dynamic suffixes like -ubb, -xyz)
            ("input[id^='add-to-cart-button']", "ID prefix (dynamic suffix)"),

            # 3. Any element with ID starting with prefix (catches both input and button)
            ("[id^='add-to-cart-button']", "ID prefix (any element)"),

            # 4. Input by exact text - "Add to Cart"
            ("input:has-text('Add to Cart')", "text 'Add to Cart'"),

            # 5. Input by exact text - "Add to basket" (UK/EU variation)
            ("input:has-text('Add to basket')", "text 'Add to basket'"),

            # 6. Button by exact text - "Add to Cart"
            ("button:has-text('Add to Cart')", "button with text 'Add to Cart'"),

            # 7. Button by exact text - "Add to basket"
            ("button:has-text('Add to basket')", "button with text 'Add to basket'"),

            # 8. Any element with "Add to Cart" text (broadest fallback)
            (":has-text('Add to Cart')", "any element with 'Add to Cart'"),

            # 9. Any element with "Add to basket" text (broadest fallback)
            (":has-text('Add to basket')", "any element with 'Add to basket'"),
        ]

        # Try each selector strategy
        print("Searching for add-to-cart/basket button...")
        button_found = False
        button_locator = None
        matched_strategy = None

        for selector, strategy_name in button_selectors:
            try:
                button_locator = page.locator(selector).first
                if button_locator.is_visible(timeout=2000):
                    print(f"✓ Found button using: {strategy_name}")
                    print(f"  Selector: {selector}")
                    button_found = True
                    matched_strategy = strategy_name
                    break
            except Exception:
                # Selector not found or not visible, try next one
                continue

        if not button_found:
            print("✗ Button not found with any selector strategy")
            print("  Attempted strategies:")
            for _, strategy_name in button_selectors:
                print(f"    - {strategy_name}")
            return False

        # Click the button
        print(f"Clicking add-to-cart/basket button...")
        button_locator.click()

        print(f"✓ Successfully clicked add-to-cart/basket button (matched: {matched_strategy})")
        time.sleep(5)
        
        return True

    except PlaywrightTimeoutError:
        print("✗ Timeout: Add-to-cart/basket button not found or not visible")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Main function to process multiple product URLs."""

    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(headless=False, channel="msedge")

        # Create context with fixed viewport for consistency
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )

        # List of product URLs to process
        cart = [
            "https://www.amazon.fr/-/en/JBL-Wireless-Headphones-Adaptive-Cancelling/dp/B09CYX92NB?pd_rd_w=RKAbJ&content-id=amzn1.sym.284f37d8-e6cd-4216-9f25-ad7ef67b15ed&pf_rd_p=284f37d8-e6cd-4216-9f25-ad7ef67b15ed&pf_rd_r=V1G2ET69GYAQ4HHJN3E6&pd_rd_wg=IccB9&pd_rd_r=24b69cef-22c5-4ecb-b8eb-daacfe34f62d&pd_rd_i=B09CYX92NB&th=1",
            "https://www.amazon.fr/-/en/Remember-me/dp/B0098VWTT2?crid=2G2RPG5AQLO65&dib=eyJ2IjoiMSJ9.sn8xt4H4e5DIIrfCJJpVh70cFt3PnpnT4K88ZJ3IRbhHNqZCj4pC073gy0XiYzdTbVW5e2ACinL1Tr4iomiwKX-6J_tYOCs683U79GLUlL0.Wg80dgXML8MZRQbvCihN6h2sFBRcWLM8JXJ4MI6IS_E&dib_tag=se&keywords=remember+me+xbox+360&qid=1769640266&sprefix=remember+me+xbox%2Caps%2C215&sr=8-1",
        ]

        # Process each URL
        success_count = 0
        page = context.new_page()

        for url in cart:
            if add_to_cart(page, url):
                success_count += 1

        page.close()

        # Summary
        print(f"\n{'=' * 50}")
        print(f"Completed: {success_count}/{len(cart)} products added to cart")
        print(f"{'=' * 50}")

        # Cleanup
        browser.close()


if __name__ == "__main__":
    main()
