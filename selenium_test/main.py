import os
import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image, ImageDraw, ImageChops, ImageStat
from io import BytesIO
import numpy as np
import easyocr


reader = easyocr.Reader(['en'])
driver = webdriver.Firefox()
driver.get("file://" + os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html"))

elem = driver.find_element_by_id("env")
last_img = None
last_scanned_img = None

def image_diff(img1, img2):
    if img1.mode != img2.mode or img1.size != img2.size or img1.getbands() != img2.getbands():
        return 1.0
    diff = ImageChops.difference(img1, img2)
    if not diff.getbbox():
        return 0.0
    stat = ImageStat.Stat(diff)
    diff_ratio = sum(stat.mean) / (len(stat.mean) * 255)
    print(diff_ratio)
    return diff_ratio

PAUSE_TIME = 1

while True:
    # Take a screenshot and crop it
    png = driver.get_screenshot_as_png()
    img = Image.open(BytesIO(png)).convert("RGB")
    img = img.crop((0, 0, elem.size["width"], elem.size["height"]))
    if img.size[0] == 0 or img.size[1] == 0:
        time.sleep(PAUSE_TIME)
        continue

    # Check if the image is stable (no movement)
    if last_img:
        if image_diff(last_img, img) > 0.05:
            print("Image is not stable.")
            last_img = img.copy()
            time.sleep(PAUSE_TIME)
            continue
    else:
        last_img = img.copy()
        time.sleep(PAUSE_TIME)
        continue

    # Read the text in the image
    if last_scanned_img:
        if image_diff(last_scanned_img, img) == 0:
            print("Image has not changed since last scan.")
            time.sleep(PAUSE_TIME)
            continue

    last_scanned_img = img.copy()
    print("Scanning image.")
    result = reader.readtext(np.asarray(img), min_size=5, mag_ratio=2)
    print("Scan complete.")

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
    time.sleep(PAUSE_TIME)

driver.close()