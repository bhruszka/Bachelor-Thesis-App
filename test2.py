import ImageProcessing as ip
import glob, os
os.chdir("~/testSet")
i = 1
for file in glob.glob("*.jpg"):
    print(i)
    ip.processImage(file, "~/testResults", True)
    i += 1





