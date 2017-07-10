from __future__ import print_function
from skimage.feature import peak_local_max
from skimage.morphology import watershed
from scipy import ndimage
import argparse
import cv2
import numpy as np
import math
import os.path


def makeToothPossitions(toothWidth, img, upD, downD, gapLine, center, path, bTest):
    upD = upD
    downD = downD
    global bWidth
    bWidth = True
    thisToothPossition2 = np.empty((2, 32), dtype=int)
    thisToothPossition = np.empty(img.shape, dtype=bool)
    thisToothPossition.fill(False)

    currentWidthUp = 0
    currentWidthDown = 0
    for i in range(0, toothWidth.shape[1]):
        currentWidthUp += toothWidth[0, i] / 2
        currentWidthDown += toothWidth[0, i] / 2

        thisToothPossition[upD + gapLine[int(center - int(currentWidthDown))], center - int(currentWidthUp)] = True
        thisToothPossition[downD + gapLine[int(center - int(currentWidthDown))], center - int(currentWidthDown)] = True
        thisToothPossition[upD + gapLine[int(center + int(currentWidthDown))], center + int(currentWidthUp)] = True
        thisToothPossition[downD + gapLine[int(center + int(currentWidthDown))], center + int(currentWidthDown)] = True

        thisToothPossition2[0][7 - i] = upD + gapLine[int(center - int(currentWidthDown))]
        thisToothPossition2[1][7 - i] = center - int(currentWidthUp)

        thisToothPossition2[0][8 + i] = downD + gapLine[int(center - int(currentWidthDown))]
        thisToothPossition2[1][8 + i] = center - int(currentWidthDown)

        thisToothPossition2[0][23 - i] = upD + gapLine[int(center + int(currentWidthDown))]
        thisToothPossition2[1][23 - i] = center + int(currentWidthUp)

        thisToothPossition2[0][24 + i] = downD + gapLine[int(center + int(currentWidthDown))]
        thisToothPossition2[1][24 + i] = center + int(currentWidthDown)

        currentWidthUp += toothWidth[0, i] / 2
        currentWidthDown += toothWidth[0, i] / 2



    # if not bTest:
    #     np.savetxt(path, thisToothPossition2, delimiter=' ')

    return thisToothPossition2


def makeWaterShed(img, toothWidth, upD, downD, gapLine, center, path, backGround, bTest):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    fileName = path + "//" + "toothCoordinates.out"
    thisToothPossition = makeToothPossitions(toothWidth, gray, upD, downD, gapLine, center, fileName, bTest)
    img = generateGrid(toothWidth, img, upD, downD, gapLine, center, path, bTest)
    imgcopy = np.copy(img)
    img = cv2.morphologyEx(img, cv2.MORPH_OPEN,
                           np.ones((5, 5), dtype=int))

    shifted = cv2.pyrMeanShiftFiltering(img, 3, 3)

    thresh = cv2.cvtColor(shifted.astype(np.uint8), cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(thresh, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]


    thresh = cv2.bitwise_and(thresh, thresh, mask=np.uint8(backGround))
    # if not bTest:
    #     cv2.imwrite(path + "//" + "thresh.jpg", thresh)

    return waterShed(imgcopy, thisToothPossition, thresh), thresh


def redoWaterShed(img, path):
    fileName = path + "//" + "toothCoordinates.out"
    if os.path.isfile(fileName):
        thisToothPossition = np.loadtxt(fileName, dtype=np.int, delimiter=' ')
    else:
        return 1

    fileName = path + "//" + "thresh.jpg"
    if os.path.isfile(fileName):
        thresh = cv2.imread(fileName, 1)
        thresh = cv2.cvtColor(thresh, cv2.COLOR_BGR2GRAY)
    else:
        return 1
    return waterShed(img, thisToothPossition, thresh)


def waterShed(img, thisToothPossition, thresh):
    D = ndimage.distance_transform_edt(thresh)

    starts = np.empty(img.shape[0:2], dtype=int)
    starts.fill(0)

    #img = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

    for i in range(0, thisToothPossition[0].shape[0]):
        starts[thisToothPossition[0][i], thisToothPossition[1][i]] = i

        cv2.circle(img, (thisToothPossition[1][i], thisToothPossition[0][i]), 5, (0, 0, 255), 1)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, str(i), (thisToothPossition[1][i], thisToothPossition[0][i]), font, 0.5, (255, 0, 0), 2,
                    cv2.LINE_AA)

    labels = watershed(-D, starts, mask=thresh)


    for label in np.unique(labels):
        # if the label is zero, we are examining the 'background'
        # so simply ignore it

        if label == 0:
            continue

        # # otherwise, allocate memory for the label region and draw
        # # it on the mask
        mask = np.zeros(img.shape[0:2], dtype="uint8")
        mask[labels == label] = 255

        # detect contours in the mask and grab the largest one
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_NONE)[-2]
        c = max(cnts, key=cv2.contourArea)

        #cv2.drawContours(img, c, -1, [0, 255, 0], 3)
    # cv2.imshow('afterLaplace', img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return img

def generateGrid(toothWidth, img, upD, downD, gapLine, center, path, bTest):

    upD = upD
    downD = downD

    teethGrid = np.empty((2, 17, 2, 2), dtype=int)

    currentWidthUp = 0
    currentWidthDown = 0

    teethGrid[0, 8, 0, 0] = upD + gapLine[int(center)]
    teethGrid[0, 8, 0, 1] = int(center)
    teethGrid[0, 8, 1, 0] = gapLine[int(center)]
    teethGrid[0, 8, 1, 1] = int(center)

    teethGrid[1, 8, 0, 0] = downD + gapLine[int(center)]
    teethGrid[1, 8, 0, 1] = int(center)
    teethGrid[1, 8, 1, 0] = gapLine[int(center)]
    teethGrid[1, 8, 1, 1] = int(center)


    for i in range(1, 9):
        currentWidthUp += toothWidth[0, i-1]
        currentWidthDown += toothWidth[1, i-1]

        teethGrid[0, 8 - i, 0, 0] = upD + gapLine[int(center - currentWidthUp)]
        teethGrid[0, 8 - i, 0, 1] = int(center - currentWidthUp)
        teethGrid[0, 8 - i, 1, 0] = gapLine[int(center - currentWidthUp)]
        teethGrid[0, 8 - i, 1, 1] = int(center - currentWidthUp)

        teethGrid[0, 8 + i, 0, 0] = upD + gapLine[int(center + currentWidthUp)]
        teethGrid[0, 8 + i, 0, 1] = int(center + currentWidthUp)
        teethGrid[0, 8 + i, 1, 0] = gapLine[int(center + currentWidthUp)]
        teethGrid[0, 8 + i, 1, 1] = int(center + currentWidthUp)

        teethGrid[1, 8 - i, 0, 0] = downD + gapLine[int(center - currentWidthDown)]
        teethGrid[1, 8 - i, 0, 1] = int(center - currentWidthDown)
        teethGrid[1, 8 - i, 1, 0] = gapLine[int(center - currentWidthDown)]
        teethGrid[1, 8 - i, 1, 1] = int(center - currentWidthDown)

        teethGrid[1, 8 + i, 0, 0] = downD + gapLine[int(center + currentWidthDown)]
        teethGrid[1, 8 + i, 0, 1] = int(center + currentWidthDown)
        teethGrid[1, 8 + i, 1, 0] = gapLine[int(center + currentWidthDown)]
        teethGrid[1, 8 + i, 1, 1] = int(center + currentWidthDown)

    return drawGrid(img, teethGrid)

def drawGrid(img, teethGrid):
    #return
    if teethGrid.shape != (2, 17, 2, 2):
        print("Wrong size")

    currentPointsUpLeft = np.array(teethGrid[0,8,:,:])
    currentPointsUpRight = np.array(teethGrid[0, 8, :, :])

    currentPointsDownLeft = np.array(teethGrid[1,8,:,:])
    currentPointsDownRight = np.array(teethGrid[1, 8, :, :])

    # cv2.line(img, tuple(currentPointsUpLeft[0, ::-1]), tuple(currentPointsUpLeft[1, ::-1]), (0, 255, 0), thickness=3, lineType=8, shift=0)
    # cv2.line(img, tuple(currentPointsUpRight[0, ::-1]), tuple(currentPointsUpRight[1, ::-1]), (0, 255, 0), thickness=3, lineType=8, shift=0)
    # cv2.line(img, tuple(currentPointsDownLeft[0, ::-1]), tuple(currentPointsDownLeft[1, ::-1]), (0, 255, 0), thickness=3, lineType=8, shift=0)
    # cv2.line(img, tuple(currentPointsDownRight[0, ::-1]), tuple(currentPointsDownRight[1, ::-1]), (0, 255, 0), thickness=3, lineType=8, shift=0)
    for i in range(1, 9):

        p1 = teethGrid[0, 8-i, :, :]
        #cv2.line(img, tuple(currentPointsUpLeft[0, ::-1]), tuple(p1[0, ::-1]), (0, 0, 255), thickness=1, lineType=8, shift=0)
        cv2.line(img, tuple(currentPointsUpLeft[1, ::-1]), tuple(p1[1, ::-1]), (0, 255, 0), thickness=1, lineType=8, shift=0)
        # cv2.line(img,  tuple(p1[0, ::-1]), tuple(p1[1, ::-1]), (0, 255, 0), thickness=3, lineType=8, shift=0)
        currentPointsUpLeft = p1

        p2 = teethGrid[0, 8+i, :, :]
        #cv2.line(img, tuple(currentPointsUpRight[0, ::-1]), tuple(p2[0, ::-1]), (0, 0, 255), thickness=1, lineType=8, shift=0)
        cv2.line(img, tuple(currentPointsUpRight[1, ::-1]), tuple(p2[1, ::-1]), (0, 255, 0), thickness=1, lineType=8, shift=0)
        # cv2.line(img, tuple(p2[0, ::-1]), tuple(p2[1, ::-1]), (0, 255, 0), thickness=3, lineType=8, shift=0)
        currentPointsUpRight = p2

        p3 = teethGrid[1, 8-i, :, :]
        #cv2.line(img, tuple(currentPointsDownLeft[0, ::-1]), tuple(p3[0, ::-1]), (0,0,255), thickness=1, lineType=8, shift=0)
        cv2.line(img, tuple(currentPointsDownLeft[1, ::-1]), tuple(p3[1, ::-1]), (0, 255, 0), thickness=1, lineType=8, shift=0)
        # cv2.line(img, tuple(p3[0, ::-1]), tuple(p3[1, ::-1]), (0, 255, 0), thickness=3, lineType=8, shift=0)
        currentPointsDownLeft = p3

        p4 = teethGrid[1, 8+i, :, :]
        #cv2.line(img, tuple(currentPointsDownRight[0, ::-1]), tuple(p4[0, ::-1]), (0,0,255), thickness=1, lineType=8, shift=0)
        cv2.line(img, tuple(currentPointsDownRight[1, ::-1]), tuple(p4[1, ::-1]), (0, 255, 0), thickness=1, lineType=8, shift=0)
        # cv2.line(img, tuple(p4[0, ::-1]), tuple(p4[1, ::-1]), (0, 255, 0), thickness=3, lineType=8, shift=0)
        currentPointsDownRight = p4

    return img
