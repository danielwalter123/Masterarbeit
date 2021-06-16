from PIL import Image, ImageChops, ImageStat

img1 = Image.open("./screenshots/03.png").convert("RGB")
img2 = Image.open("./screenshots/08.png").convert("RGB")

diff = ImageChops.difference(img1, img2)

stat = ImageStat.Stat(diff)
diff_ratio = sum(stat.mean) / (len(stat.mean) * 255)
print(diff_ratio)