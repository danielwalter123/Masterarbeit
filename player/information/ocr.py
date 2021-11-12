import time
import easyocr
from PIL import Image, ImageChops, ImageStat
import numpy as np
import importlib
import config

system = importlib.import_module("systems." + config.system)
reader = easyocr.Reader(['en'])

OCR_FIX = {
    "ok": ["ok", "tk", "0k"],
    "file": ["file", "eile"]
}

PAUSE_TIME = 1

last_img = None
last_scanned_img = None
last_result = None

# Scans the screen and returns the result.
def _scan():
    global last_img, last_scanned_img, last_result

    # Wait for the image to be stable by taking a screenshot every second
    # and comapring it to the last one.
    while True:
        img = system.screenshot()
        if last_img:
            if _image_diff(last_img, img) > 0.05:
                print("Image is not stable.")
                last_img = img.copy()
                time.sleep(PAUSE_TIME)
                continue
        else:
            last_img = img.copy()
            time.sleep(PAUSE_TIME)
            continue
        break
    
    # Return the last result if the image is the same as the last one.
    if last_scanned_img and _image_diff(last_scanned_img, img) == 0 and last_result:
        return last_result

    # Scan the image for text
    last_scanned_img = img.copy()
    print("Scanning image.")
    last_result = reader.readtext(np.asarray(img), decoder="wordbeamsearch",
                                  min_size=5, mag_ratio=2)
    print("Scan complete.")
    return last_result
    
# Returns the difference between two images as a percentage.
def _image_diff(img1, img2):
    if (img1.mode != img2.mode or img1.size != img2.size or
        img1.getbands() != img2.getbands()):
        return 1.0
    diff = ImageChops.difference(img1, img2)
    if not diff.getbbox():
        return 0.0
    stat = ImageStat.Stat(diff)
    diff_ratio = sum(stat.mean) / (len(stat.mean) * 255)
    return diff_ratio


# Returns the ocr result of the given text.
def _find_text(text):
    result = _scan()
    text = text.lower()
    for r in result:
        ocr_text = r[1].lower()
        if ocr_text == text or (text in OCR_FIX and ocr_text in OCR_FIX[text]):
            return r
    return None

# Returns the position of the given text.
def resolve_position(data):
    match = _find_text(data)
    if not match:
        return None
    top_left = (match[0][0][0], match[0][0][1])
    bottom_right = (match[0][2][0], match[0][2][1])
    return np.divide(np.add(top_left, bottom_right), 2)

# Waits for the given text to appear.
def wait(data):
    match = None
    while not match:
        match = _find_text(data)
        time.sleep(PAUSE_TIME)
