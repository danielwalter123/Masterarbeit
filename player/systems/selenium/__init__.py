import os
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from PIL import Image
from io import BytesIO
import config

driver = webdriver.Firefox()
driver.get("file://" + os.path.join(os.path.dirname(os.path.abspath(__file__)), config.eaas_html))
elem = driver.find_element_by_id("env")

def screenshot():
    png = driver.get_screenshot_as_png()
    img = Image.open(BytesIO(png)).convert("RGB")
    return img.crop((0, 0, elem.size["width"], elem.size["height"]))

def text(text):
    action = ActionChains(driver)
    for char in text:
        if char.isupper():
            action.key_down(Keys.SHIFT)
        action.send_keys(char)
        action.key_up(Keys.SHIFT)
        action.pause(0.1)
    action.perform()

def click(x, y):
    action = ActionChains(driver)
    action.reset_actions()
    action.move_to_element_with_offset(elem, x, y)
    action.click()
    action.perform()
