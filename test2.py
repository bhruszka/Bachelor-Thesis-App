import ImageProcessing as ip
import glob, os
os.chdir("root\\testSet")
i = 1
for file in glob.glob("*.jpg"):
    print(i)
    ip.processImage(file, "root\\testResults\\", True)
    i += 1





