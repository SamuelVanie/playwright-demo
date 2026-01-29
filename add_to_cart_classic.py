"""
Add to Cart - Classic Playwright Approach
Uses direct DOM interaction instead of computer vision.
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


def add_to_cart(page, url):
    """
    Navigate to a product page and click the add-to-cart button using DOM selectors.
    
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
        
        # Wait for the add-to-cart button to be visible
        # Using the class name provided: 'add-to-cart-button'
        print("Waiting for add-to-cart button...")
        page.wait_for_selector(
            ".add-to-cart-button",
            state="visible",
            timeout=15000
        )
        
        # Click the button using direct DOM interaction
        print("Clicking add-to-cart button...")
        page.locator(".add-to-cart-button").click()
        
        print("✓ Successfully clicked add-to-cart button")
        return True
        
    except PlaywrightTimeoutError:
        print("✗ Timeout: Add-to-cart button not found or not visible")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Main function to process multiple product URLs."""
    
    with sync_playwright() as p:
        # Launch browser in headless mode
        browser = p.chromium.launch(
            headless=True,
            channel="msedge"
        )
        
        # Create context with fixed viewport for consistency
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # List of product URLs to process
        cart = [
            "https://www.amazon.fr/-/en/JBL-Wireless-Headphones-Adaptive-Cancelling/dp/B09CYX92NB?pd_rd_w=RKAbJ&content-id=amzn1.sym.284f37d8-e6cd-4216-9f25-ad7ef67b15ed&pf_rd_p=284f37d8-e6cd-4216-9f25-ad7ef67b15ed&pf_rd_r=V1G2ET69GYAQ4HHJN3E6&pd_rd_wg=IccB9&pd_rd_r=24b69cef-22c5-4ecb-b8eb-daacfe34f62d&pd_rd_i=B09CYX92NB&th=1",
            "https://www.amazon.fr/-/en/Remember-me/dp/B0098VWTT2?crid=2G2RPG5AQLO65&dib=eyJ2IjoiMSJ9.sn8xt4H4e5DIIrfCJJpVh70cFt3PnpnT4K88ZJ3IRbhHNqZCj4pC073gy0XiYzdTbVW5e2ACinL1Tr4iomiwKX-6J_tYOCs683U79GLUlL0.Wg80dgXML8MZRQbvCihN6h2sFBRcWLM8JXJ4MI6IS_E&dib_tag=se&keywords=remember+me+xbox+360&qid=1769640266&sprefix=remember+me+xbox%2Caps%2C215&sr=8-1"
        ]
        
        # Process each URL
        success_count = 0
        for url in cart:
            page = context.new_page()
            if add_to_cart(page, url):
                success_count += 1
            page.close()
        
        # Summary
        print(f"\n{'='*50}")
        print(f"Completed: {success_count}/{len(cart)} products added to cart")
        print(f"{'='*50}")
        
        # Cleanup
        browser.close()


if __name__ == "__main__":
    main()
