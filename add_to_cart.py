import cv2
import numpy as np
import time
from playwright.sync_api import sync_playwright

def find_image_coordinates(page, template_path, threshold=0.8):
    """
    Core Vision Function:
    - Takes a screenshot in memory (no disk I/O).
    - Converts to Grayscale for 3x speedup.
    - Matches template.
    """
    try:
        # 1. Take screenshot directly to memory
        screenshot_bytes = page.screenshot()
        
        # 2. Convert to format OpenCV understands
        nparr = np.frombuffer(screenshot_bytes, np.uint8)
        img_screen = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # 3. OPTIMIZATION: Convert to Grayscale
        # This reduces data by 66% and speeds up matching significantly
        screen_gray = cv2.cvtColor(img_screen, cv2.COLOR_BGR2GRAY)
        
        # Load template and convert to grayscale
        template = cv2.imread(template_path)
        if template is None:
            print(f"Error: Could not load image at {template_path}")
            return None
            
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        
        # 4. Match Template
        result = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # 5. Check Threshold
        if max_val >= threshold:
            h, w = template_gray.shape
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            return {"x": center_x, "y": center_y, "val": max_val}
            
        return None

    except Exception as e:
        print(f"Vision Error: {e}")
        return None

def visual_click(page, template_path, wait_for_selector=None):
    """
    Logic Wrapper:
    - Handles the 'Wait + One-Shot + Retry' logic.
    - safe-guards against rendering lag.
    """
    
    # A. Wait for a DOM Element (The "Hybrid Trigger")
    # If provided, we wait for a specific HTML element to exist before we look with our eyes.
    if wait_for_selector:
        try:
            page.locator(wait_for_selector).wait_for(state="visible", timeout=10000)
        except:
            print(f"Warning: Selector {wait_for_selector} timed out. Proceeding anyway...")

    # B. The "Render Buffer"
    # Even if DOM is ready, Canvas/WebGL might need 500ms to paint pixels.
    # This sleep is cheap and prevents false negatives.
    time.sleep(0.5) 
    
    # C. Attempt 1 (The Fast Path)
    print(f"Scanning for {template_path}...")
    coords = find_image_coordinates(page, template_path)
    
    # D. Attempt 2 (The Retry / Safety Net)
    # If failed, we assume it's a slow render or animation. Wait 1s and try ONE more time.
    if not coords:
        print("Image not found immediately. Waiting 1s for potential lag/animation...")
        time.sleep(1.0)
        coords = find_image_coordinates(page, template_path)

    # E. Action
    if coords:
        print(f"Found at ({coords['x']}, {coords['y']}) with confidence {coords['val']:.2f}")
        # Move mouse naturally before clicking (helps avoid bot detection)
        page.mouse.move(coords['x'], coords['y'])
        page.mouse.click(coords['x'], coords['y'])
        return True
    else:
        print("Image failed to appear after retry.")
        return False

def main():
    
    with sync_playwright() as p:
        # 1. Server Optimization: Headless is faster
        browser = p.chromium.launch(headless=True, channel="msedge")

        # List of the articles to add to the cart
        cart = ["https://www.amazon.fr/-/en/JBL-Wireless-Headphones-Adaptive-Cancelling/dp/B09CYX92NB?pd_rd_w=RKAbJ&content-id=amzn1.sym.284f37d8-e6cd-4216-9f25-ad7ef67b15ed&pf_rd_p=284f37d8-e6cd-4216-9f25-ad7ef67b15ed&pf_rd_r=V1G2ET69GYAQ4HHJN3E6&pd_rd_wg=IccB9&pd_rd_r=24b69cef-22c5-4ecb-b8eb-daacfe34f62d&pd_rd_i=B09CYX92NB&th=1", "https://www.amazon.fr/-/en/Remember-me/dp/B0098VWTT2?crid=2G2RPG5AQLO65&dib=eyJ2IjoiMSJ9.sn8xt4H4e5DIIrfCJJpVh70cFt3PnpnT4K88ZJ3IRbhHNqZCj4pC073gy0XiYzdTbVW5e2ACinL1Tr4iomiwKX-6J_tYOCs683U79GLUlL0.Wg80dgXML8MZRQbvCihN6h2sFBRcWLM8JXJ4MI6IS_E&dib_tag=se&keywords=remember+me+xbox+360&qid=1769640266&sprefix=remember+me+xbox%2Caps%2C215&sr=8-1"]
        
        # 2. CRITICAL OPTIMIZATION: Fix Resolution
        # We force device_scale_factor=1 so 1 CSS pixel = 1 Screen pixel.
        # This prevents Retina/HighDPI displays from breaking coordinate math.
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            device_scale_factor=1 
        )

        for page in cart:
            add_to_cart(context, page)

        # Cleanup
        browser.close()



def add_to_cart(context, link):
    page = context.new_page()
    # Example: Google Maps or a Game
    page.goto(link)

    # USAGE SCENARIO:
    # We want to click a button, but we wait for the canvas to load first.
    # pass `wait_for_selector` to ensure the "container" is there.
    # (For Maps, 'canvas' is usually the map container)

    # Assuming you have an image called 'product1.png'
    success = visual_click(page, "product1.png", wait_for_selector="canvas")

    if success:
        print("Action completed successfully.")
    else:
        print("Action failed.")

if __name__ == "__main__":
    main()
