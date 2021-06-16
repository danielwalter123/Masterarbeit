import os
import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image, ImageDraw, ImageChops
from io import BytesIO
import numpy as np
import easyocr


reader = easyocr.Reader(['en'])
driver = webdriver.Firefox()
driver.get("file://" + os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html"))

elem = driver.find_element_by_id("env")
last_img = None
last_scanned_img = None

while True:
    # Take a screenshot and crop it
    png = driver.get_screenshot_as_png()
    img = Image.open(BytesIO(png)).convert("RGB")
    img = img.crop((0, 0, elem.size["width"], elem.size["height"]))

    # Check if the image is stable (no movement)
    if last_img:
        diff = ImageChops.difference(last_img, img)
        if diff.getbbox():
            print("Image is not stable.")
            last_img = img.copy()
            time.sleep(0.5)
            continue
    else:
        last_img = img.copy()
        continue

    # Read the text in the image
    if last_scanned_img:
        diff = ImageChops.difference(last_scanned_img, img)
        if not diff.getbbox():
            print("Image has not changed since last scan.")
            time.sleep(0.5)
            continue

    last_scanned_img = img.copy()
    print("Scanning image.")
    result = reader.readtext(np.asarray(img), min_size=5, mag_ratio=2)

    for r in result:
        print(r[1])
        draw = ImageDraw.Draw(img)
        top_left = (r[0][0][0], r[0][0][1])
        bottom_right = (r[0][2][0], r[0][2][1])
        draw.rectangle((top_left, bottom_right), outline="red")

        if r[1].lower() in ["ok", "0k", "tk"]:
            center = np.divide(np.add(top_left, bottom_right), 2)
            action = ActionChains(driver)
            action.reset_actions()
            action.move_to_element_with_offset(elem, center[0], center[1])
            action.click()
            action.perform()

    #img.show()

driver.close()