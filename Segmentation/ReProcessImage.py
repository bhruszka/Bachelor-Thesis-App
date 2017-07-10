import argparse
import cv2
import Segmentation as sg
import os.path
from Segmentation import ImageTranformation as iT
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--ReadPath", required = True, help = "Path to the image")
parser.add_argument("-w", "--WritePath", required = True, help = "Path to the save dir")

args = vars(parser.parse_args())
dirName, imageHead = os.path.split(args["ReadPath"])
imageName = os.path.splitext(imageHead)[0]
saveFolderDir = args["WritePath"] + "/" + imageName
if not os.path.exists(saveFolderDir):
    os.makedirs(saveFolderDir)

img = cv2.imread(args["ReadPath"], 1)
img = iT.cutImage(img)

hFactor = 1000 / img.shape[0]

img = cv2.resize(img, (0, 0), fx=hFactor, fy=hFactor)
tempImg = np.empty((img.shape[0] + 16 - (img.shape[0] % 16), img.shape[1] + 16 - (img.shape[1] % 16), 3), dtype=np.uint8)
tempImg.fill(0)
tempImg[0:img.shape[0], 0:img.shape[1], 0:3] = img
img = np.array(tempImg, copy=True)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

resultImage = sg.redoWaterShed(img, saveFolderDir)
cv2.imwrite(saveFolderDir + "/" + "segmentedImage.jpg", resultImage)
