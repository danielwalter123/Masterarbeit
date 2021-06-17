import os
import time
import yaml
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from PIL import Image, ImageDraw, ImageChops, ImageStat
from io import BytesIO
import numpy as np
import easyocr


# Read yaml file
steps = None
with open("example.yaml", 'r') as stream:
    try:
        steps = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

if not steps or type(steps) is not list:
    exit()

reader = easyocr.Reader(['en'])
driver = webdriver.Firefox()
driver.get("file://" + os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html"))

def image_diff(img1, img2):
    if img1.mode != img2.mode or img1.size != img2.size or img1.getbands() != img2.getbands():
        return 1.0
    diff = ImageChops.difference(img1, img2)
    if not diff.getbbox():
        return 0.0
    stat = ImageStat.Stat(diff)
    diff_ratio = sum(stat.mean) / (len(stat.mean) * 255)
    return diff_ratio


OCR_FIX = {
    "ok": ["ok", "tk", "0k"],
    "file": ["file", "eile"]
}

PAUSE_TIME = 1
elem = driver.find_element_by_id("env")
last_img = None
last_scanned_img = None

step = steps.pop(0)
while step:
    print("Next step: " + str(step))

    if type(step) is not list or len(step) < 2:
        print("Invalid step!")
        continue

    if step[0] == "input":
        time.sleep(3)
        action = ActionChains(driver)
        for char in step[1]:
            if char.isupper():
                action.key_down(Keys.SHIFT)
            action.send_keys(char)
            action.key_up(Keys.SHIFT)
            action.pause(0.1)
        action.perform()
        step = steps.pop(0) if len(steps) > 0 else None
        continue

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
    result = reader.readtext(np.asarray(img), decoder="wordbeamsearch", min_size=5, mag_ratio=2)
    print("Scan complete.")

    for r in result:
        print(r[1])
        draw = ImageDraw.Draw(img)
        top_left = (r[0][0][0], r[0][0][1])
        bottom_right = (r[0][2][0], r[0][2][1])
        draw.rectangle((top_left, bottom_right), outline="red")

        ocr_text = r[1].lower()
        step_text = step[1].lower()

        if ocr_text == step_text or (step_text in OCR_FIX and ocr_text in OCR_FIX[step_text]):
            center = np.divide(np.add(top_left, bottom_right), 2)
            action = ActionChains(driver)
            action.reset_actions()
            action.move_to_element_with_offset(elem, center[0], center[1])
            action.click()
            action.perform()
            step = steps.pop(0) if len(steps) > 0 else None
            break

    #img.show()
    time.sleep(PAUSE_TIME)

#driver.close()
