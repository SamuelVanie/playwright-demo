import cv2
import numpy as np
from playwright.sync_api import sync_playwright

def find_image_on_page(page, image_path, threshold=0.8):
    # 1. Take a screenshot of the page in memory
    screenshot_bytes = page.screenshot()
    
    # 2. Convert raw bytes to a numpy array for OpenCV
    nparr = np.frombuffer(screenshot_bytes, np.uint8)
    img_screen = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # 3. Load the "needle" image you want to find
    img_template = cv2.imread(image_path)
    
    # 4. Match the template
    result = cv2.matchTemplate(img_screen, img_template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    # 5. Check if the match is good enough
    if max_val >= threshold:
        # Get dimensions to click the center
        h, w = img_template.shape[:2]
        center_x = max_loc[0] + w // 2
        center_y = max_loc[1] + h // 2
        return {"x": center_x, "y": center_y, "found": True}
    
    return {"found": False}

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=False)
    page = browser.new_page()
    page.goto("https://www.google.com")

    # search_icon.png the name of the image representing the button to click on
    coords = find_image_on_page(page, "search_icon.png")

    if coords["found"]:
        print(f"Found at: {coords['x']}, {coords['y']}")
        # Use Playwright's mouse to click coordinates naturally
        page.mouse.move(coords["x"], coords["y"])
        page.mouse.click(coords["x"], coords["y"])
    else:
        print("Image not found.")

    browser.close()
