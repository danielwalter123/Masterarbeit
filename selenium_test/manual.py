import os
import time
from selenium import webdriver
from PIL import Image, ImageDraw
from io import BytesIO
import numpy as np
import easyocr


reader = easyocr.Reader(['en'])
driver = webdriver.Firefox()
driver.get("file://" + os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html"))


elem = driver.find_element_by_id("env")

while True:
    x = input("Press Enter to scan the image... ")
    if x == "q":
        break

    # Take a screenshot and crop it
    png = driver.get_screenshot_as_png()
    img = Image.open(BytesIO(png)).convert("RGB")
    img = img.crop((0, 0, elem.size["width"], elem.size["height"]))
    if img.size[0] == 0 or img.size[1] == 0:
        continue

    # Read the text in the image
    print("Scanning image.")
    result = reader.readtext(np.asarray(img), decoder="wordbeamsearch", min_size=5, mag_ratio=2)
    print("Scan complete.")

    for r in result:
        print(r[1])
        draw = ImageDraw.Draw(img)
        top_left = (r[0][0][0], r[0][0][1])
        bottom_right = (r[0][2][0], r[0][2][1])
        draw.rectangle((top_left, bottom_right), outline="red")

    img.show()


driver.close()
