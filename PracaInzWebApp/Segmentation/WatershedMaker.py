from __future__ import print_function
from skimage.feature import peak_local_max
from skimage.morphology import watershed
from scipy import ndimage
import argparse
import cv2
import numpy as np
import math
import os.path


def makeToothPossitions(toothWidth, img, upD, downD, gapLine, gapLineSlope, center, gray):
    upD = upD
    downD = downD
    global bWidth
    bWidth = True
    thisToothPossition2 = np.empty((4, 32), dtype=int)
    thisToothPossition = np.empty(img.shape, dtype=bool)
    thisToothPossition.fill(False)

    current_width_up = 0
    current_width_down = 0

    d_upD = int(6 * upD / 10)
    u_upD = int(upD)
    d_downD = int(6 * downD / 10)
    u_downD = int(downD)


    mask = np.empty(gray.shape)
    mask.fill(0)
    masked = np.empty(gray.shape)
    mask.fill(0)
    for i in range(0, toothWidth.shape[1]):
        correction_area_radius_up = int(toothWidth[0, i] / 10)
        correction_area_radius_down = int(toothWidth[1, i] / 10)

        current_width_up += toothWidth[0, i] / 2
        current_width_down += toothWidth[1, i] / 2

        current_width_up_right = int(center + current_width_up)
        current_width_up_left = int(center - current_width_up)
        current_width_down_right = int(center + current_width_down)
        current_width_down_left = int(center - current_width_down)

        # Up left:
        #
        mask.fill(0)
        cv2.circle(mask, (current_width_up_left, d_upD + gapLine[current_width_up_left]), correction_area_radius_up, 255, -1)
        masked = cv2.bitwise_and(gray, gray, mask=np.uint8(mask))
        m1, m0 = np.unravel_index(masked.argmax(), mask.shape)
        thisToothPossition2[0][7 - i] = m1
        thisToothPossition2[1][7 - i] = m0

        mask.fill(0)
        cv2.circle(mask, (current_width_up_left, u_upD + gapLine[current_width_up_left]), correction_area_radius_up,
                   255, -1)
        masked = cv2.bitwise_and(gray, gray, mask=np.uint8(mask))
        m1, m0 = np.unravel_index(masked.argmax(), mask.shape)
        thisToothPossition2[2][7 - i] = m1
        thisToothPossition2[3][7 - i] = m0


        mask.fill(0)
        cv2.circle(mask, (current_width_down_left, d_downD + gapLine[current_width_down_left]), correction_area_radius_down,
                   255, -1)
        masked = cv2.bitwise_and(gray, gray, mask=np.uint8(mask))
        m1, m0 = np.unravel_index(masked.argmax(), mask.shape)
        thisToothPossition2[0][8 + i] = m1
        thisToothPossition2[1][8 + i] = m0

        mask.fill(0)
        cv2.circle(mask, (current_width_down_left, u_downD + gapLine[current_width_down_left]), correction_area_radius_down,
                   255, -1)
        masked = cv2.bitwise_and(gray, gray, mask=np.uint8(mask))
        m1, m0 = np.unravel_index(masked.argmax(), mask.shape)
        thisToothPossition2[2][8 + i] = m1
        thisToothPossition2[3][8 + i] = m0


        mask.fill(0)
        cv2.circle(mask, (current_width_up_right, d_upD + gapLine[current_width_up_right]), correction_area_radius_up,
                   255, -1)
        masked = cv2.bitwise_and(gray, gray, mask=np.uint8(mask))
        m1, m0 = np.unravel_index(masked.argmax(), mask.shape)
        thisToothPossition2[0][23 - i] = m1
        thisToothPossition2[1][23 - i] = m0

        mask.fill(0)
        cv2.circle(mask, (current_width_up_right,  u_upD + gapLine[current_width_up_right]), correction_area_radius_up,
                   255, -1)
        masked = cv2.bitwise_and(gray, gray, mask=np.uint8(mask))
        m1, m0 = np.unravel_index(masked.argmax(), mask.shape)
        thisToothPossition2[2][23 - i] = m1
        thisToothPossition2[3][23 - i] = m0


        mask.fill(0)
        cv2.circle(mask, (current_width_down_right, d_downD + gapLine[current_width_down_right]), correction_area_radius_down,
                   255, -1)
        masked = cv2.bitwise_and(gray, gray, mask=np.uint8(mask))
        m1, m0 = np.unravel_index(masked.argmax(), mask.shape)
        thisToothPossition2[0][24 + i] = m1
        thisToothPossition2[1][24 + i] = m0

        mask.fill(0)
        cv2.circle(mask, (current_width_down_right, u_downD + gapLine[current_width_down_right]), correction_area_radius_down,
                   255, -1)
        masked = cv2.bitwise_and(gray, gray, mask=np.uint8(mask))
        m1, m0 = np.unravel_index(masked.argmax(), mask.shape)
        thisToothPossition2[2][24 + i] = m1
        thisToothPossition2[3][24 + i] = m0

        current_width_up += toothWidth[0, i] / 2
        current_width_down += toothWidth[1, i] / 2

    return thisToothPossition2


def makeWaterShed(img, toothWidth, upD, downD, gapLine, gapLineSlope, center, backGround):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.morphologyEx(img, cv2.MORPH_OPEN, np.ones((5, 5), dtype=int))
    shifted = cv2.pyrMeanShiftFiltering(img, 5, 5)

    thresh = cv2.cvtColor(shifted.astype(np.uint8), cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(thresh, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    thresh = cv2.bitwise_and(thresh, thresh, mask=np.uint8(backGround))
    gray_shifted = cv2.cvtColor(shifted, cv2.COLOR_RGB2GRAY)
    thisToothPossition = makeToothPossitions(toothWidth, gray, upD, downD, gapLine, gapLineSlope, center, gray)

    return waterShed(img, thisToothPossition, thresh)


def waterShed(img, thisToothPossition, thresh):
    D = ndimage.distance_transform_edt(thresh)

    starts = np.empty(img.shape[0:2], dtype=int)
    starts.fill(0)
    img_copy = np.copy(img)

    for i in range(0, thisToothPossition[0].shape[0]):

        # starts[thisToothPossition[0][i], thisToothPossition[1][i]] = i
        delta_y = thisToothPossition[0, i] - thisToothPossition[2, i]
        delta_x = thisToothPossition[1, i] - thisToothPossition[3, i]
        print("{} {} {}".format(i, delta_y, delta_x))
        if abs(delta_y) >= 1 or abs(delta_x) >= 1:
            if abs(delta_y) > abs(delta_x):
                d_x = delta_x / delta_y
                for j in range(0, delta_y, int(delta_y // abs(delta_y))):
                    this_y = thisToothPossition[2, i] + j
                    this_x = thisToothPossition[3, i] + int(j * d_x)
                    starts[this_y, (this_x - 2):(this_x + 3)] = (i + 1)
                    img[this_y, (this_x - 2):(this_x + 3)] = (0, 0, 255)

            else:
                d_y = delta_y / delta_x
                for j in range(0, int(delta_x), int(delta_x / abs(delta_x))):
                    this_y = thisToothPossition[2, i] + int(j * d_y)
                    this_x = thisToothPossition[3, i] + j
                    starts[(this_y - 2):(this_y + 3), this_x] = (i + 1)
                    img[(this_y - 2):(this_y + 3), this_x] = (0, 0, 255)

        cv2.circle(img, (thisToothPossition[1][i], thisToothPossition[0][i]), 5, (0, 0, 255), 2)
        cv2.circle(img, (thisToothPossition[3][i], thisToothPossition[2][i]), 5, (0, 0, 255), 2)
        # cv2.putText(img, teeth_id + "B", (thisToothPossition[3s][i], thisToothPossition[2][i]), font, 0.5, (255, 0, 0),
        #             2,
        #             cv2.LINE_AA)

    labels = watershed(-D, starts, mask=thresh)

    teethImages = [None] * 32
    bTeeth = [0] * 32
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

        if label in range(1, 33):
            x, y, w, h = cv2.boundingRect(c)
            # TODO: don't hardcode
            if w > 10 and h > 10:
                # teethImages[label-1] = cv2.bitwise_and(img_copy, img_copy, mask = mask)[y:(y+h), x:(x+w)]

                temp_tooth_image = img_copy[y:(y + h), x:(x + w)]
                if np.average(temp_tooth_image) > 80:
                    teethImages[label - 1] = temp_tooth_image
                    cv2.drawContours(img, c, -1, [0, 255, 0], 2)
                    bTeeth[label - 1] = 1
        else:
            print("Not cool label {}".format(label))
    for i in range(0, thisToothPossition[0].shape[0]):
        teeth_id = ""
        if i < 8:
            # upper left:
            teeth_num = 8 - i
            teeth_id = 'UL{}'.format(teeth_num)
        elif i < 16:
            # down left revers, don't shorten so it's readable :
            teeth_num = i - 8 + 1
            teeth_id = 'DL{}'.format(teeth_num)
        elif i < 24:
            # upper right revers:
            teeth_num = 24 - i
            teeth_id = 'UR{}'.format(teeth_num)
        elif i < 32:
            # down right:
            teeth_num = i - 24 + 1
            teeth_id = 'DR{}'.format(teeth_num)
        font = cv2.FONT_HERSHEY_PLAIN         	
        cv2.putText(img, teeth_id, ((thisToothPossition[1][i] + thisToothPossition[3][i]) // 2 - 20,
                                    (thisToothPossition[0][i] + thisToothPossition[2][i]) // 2), font, 1, (255, 0, 0),
                    2,
                    cv2.LINE_AA)
    # cv2.imshow('afterLaplace', img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    return img, thresh, thisToothPossition, bTeeth, teethImages
