import os
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image, ImageDraw
from io import BytesIO
import numpy as np
import easyocr
import cv2

reader = easyocr.Reader(['en'])
driver = webdriver.Firefox()
driver.get("file://" + os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html"))

elem = driver.find_element_by_id("env")

while True:
    check = input("Press Enter to take a screenshot...")
    if check == "q":
        break

    png = driver.get_screenshot_as_png()
    img = Image.open(BytesIO(png))
    img = img.crop((0, 0, elem.size["width"], elem.size["height"]))

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

    img.show()

driver.close()