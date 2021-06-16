from PIL import Image
from PIL import ImageChops

img1 = Image.open("./screenshots/03.png").convert("RGB")
img2 = Image.open("./screenshots/04.png").convert("RGB")

diff = ImageChops.difference(img1, img1)

diff.show()
print(diff.getbbox())