import matplotlib.pyplot as plt

import keras_ocr

pipeline = keras_ocr.pipeline.Pipeline()
img = keras_ocr.tools.read("./screenshots/03.png")
result = pipeline.recognize([img])[0]

# Plot the predictions

keras_ocr.tools.drawAnnotations(image=img, predictions=result, ax=plt.gca())
plt.show()