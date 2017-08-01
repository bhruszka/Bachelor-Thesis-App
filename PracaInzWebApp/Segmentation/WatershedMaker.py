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
    thisToothPossition2 = np.empty((4, 32), dtype=int)
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
        thisToothPossition2[2][7 - i] = upD//2 + gapLine[int(center - int(currentWidthDown))]
        thisToothPossition2[3][7 - i] = center - int(currentWidthUp)

        thisToothPossition2[0][8 + i] = downD + gapLine[int(center - int(currentWidthDown))]
        thisToothPossition2[1][8 + i] = center - int(currentWidthDown)
        thisToothPossition2[2][8 + i] = downD//2 + gapLine[int(center - int(currentWidthDown))]
        thisToothPossition2[3][8 + i] = center - int(currentWidthDown)

        thisToothPossition2[0][23 - i] = upD + gapLine[int(center + int(currentWidthDown))]
        thisToothPossition2[1][23 - i] = center + int(currentWidthUp)
        thisToothPossition2[2][23 - i] = upD//2 + gapLine[int(center + int(currentWidthDown))]
        thisToothPossition2[3][23 - i] = center + int(currentWidthUp)

        thisToothPossition2[0][24 + i] = downD + gapLine[int(center + int(currentWidthDown))]
        thisToothPossition2[1][24 + i] = center + int(currentWidthDown)
        thisToothPossition2[2][24 + i] = downD//2 + gapLine[int(center + int(currentWidthDown))]
        thisToothPossition2[3][24 + i] = center + int(currentWidthDown)

        currentWidthUp += toothWidth[0, i] / 2
        currentWidthDown += toothWidth[0, i] / 2



    # if not bTest:
    #     np.savetxt(path, thisToothPossition2, delimiter=' ')

    return thisToothPossition2


def makeWaterShed(img, toothWidth, upD, downD, gapLine, center, path, backGround, bTest):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    fileName = path + "//" + "toothCoordinates.out"
    thisToothPossition = makeToothPossitions(toothWidth, gray, upD, downD, gapLine, center, fileName, bTest)
    imgcopy = np.copy(img)
    img = cv2.morphologyEx(img, cv2.MORPH_OPEN,
                           np.ones((5, 5), dtype=int))

    shifted = cv2.pyrMeanShiftFiltering(img, 3, 3)

    thresh = cv2.cvtColor(shifted.astype(np.uint8), cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(thresh, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]


    thresh = cv2.bitwise_and(thresh, thresh, mask=np.uint8(backGround))
    # if not bTest:
    #     cv2.imwrite(path + "//" + "thresh.jpg", thresh)

    return waterShed(imgcopy, thisToothPossition, thresh)


def waterShed(img, thisToothPossition, thresh):
    D = ndimage.distance_transform_edt(thresh)

    starts = np.empty(img.shape[0:2], dtype=int)
    starts.fill(0)

    #img = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

    for i in range(0, thisToothPossition[0].shape[0]):

        #starts[thisToothPossition[0][i], thisToothPossition[1][i]] = i
        delta_y = thisToothPossition[0, i] - thisToothPossition[2, i]
        delta_x = thisToothPossition[1, i] - thisToothPossition[3, i]
        print("{} {} {}".format(i, delta_y, delta_x))
        if abs(delta_y) >= 1 or abs(delta_x) >= 1:
            if abs(delta_y) > abs(delta_x):
                d_x = delta_x / delta_y
                for j in range(0, delta_y, delta_y//abs(delta_y)):
                    this_y = thisToothPossition[2, i] + j
                    this_x = thisToothPossition[3, i] + int(j * d_x)
                    starts[this_y, this_x] = i + 1
                    img[this_y, (this_x - 2):(this_x + 2)] = (255, 0, 0)

            else:
                d_y = delta_y / delta_x
                for j in range(0, int(delta_x), int(delta_x/abs(delta_x))):
                    this_y = thisToothPossition[2, i] + int(j * d_y)
                    this_x = thisToothPossition[3, i] + j
                    starts[this_y, this_x] = i + 1
                    img[(this_y-2):(this_y+2), this_x] = (255, 0, 0)

        cv2.circle(img, (thisToothPossition[1][i], thisToothPossition[0][i]), 5, (0, 0, 255), 1)
        cv2.circle(img, (thisToothPossition[3][i], thisToothPossition[2][i]), 5, (0, 0, 255), 1)
        font = cv2.QT_FONT_LIGHT
        cv2.putText(img, str(i+1) + "A", (thisToothPossition[1][i], thisToothPossition[0][i]), font, 0.5, (255, 0, 0), 2,
                    cv2.LINE_AA)
        cv2.putText(img, str(i+1) + "B", (thisToothPossition[3][i], thisToothPossition[2][i]), font, 0.5, (255, 0, 0), 2,
                    cv2.LINE_AA)
        # TODO: draw a line:

    labels = watershed(-D, starts, mask=thresh)

    teethImages = [None] * 32
    bTeeth = [False] * 32
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

        if label in range(1,33):
            print("Label is cool")
            x, y, w, h = cv2.boundingRect(c)
            # TODO: don't hardcode
            if w in range(20, 150) and w in range(20, 150):
                print("Here is cool too")
                teethImages[label-1] = img[y:(y+h), x:(x+w)]
                #cv2.imshow('afterLaplace', teethImages[label-1])
                bTeeth[label-1] = True
        else:
            print("Not cool label {}".format(label))
        cv2.drawContours(img, c, -1, [0, 255, 0], 2)
    # cv2.imshow('afterLaplace', img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    return img, thresh, thisToothPossition, bTeeth, teethImages


