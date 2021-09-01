from PIL import Image, ImageChops, ImageStat

img1 = Image.open("../screenshots/03.png").convert("RGB")
img2 = Image.open("../screenshots/04.png").convert("RGB")

diff = ImageChops.difference(img1, img2)

diff.show()