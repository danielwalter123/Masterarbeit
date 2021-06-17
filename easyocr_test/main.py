import sys
from PIL import Image
import numpy as np
import cv2
import easyocr

from tkinter import Tk
from tkinter.filedialog import askopenfilename
Tk().withdraw()

print("init")

reader = easyocr.Reader(['en'])

print("ready")

while True:
    print("###############################################")
    path = askopenfilename()
    
    image = Image.open(path)
    data = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)
    
    result = reader.readtext(data, decoder="wordbeamsearch", min_size=5, mag_ratio=2)

    for r in result:
        print(r[1])
        cv2.rectangle(data, (int(r[0][0][0]), int(r[0][0][1])), (int(r[0][2][0]), int(r[0][2][1])), (0, 0, 255), 2)

    cv2.imshow("Image", data)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
